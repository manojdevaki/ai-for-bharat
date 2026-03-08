"""Web API handler for Sookshma AI web interface"""
import json
import base64
import os
import boto3
from typing import Dict, Any
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from services.ingredient.processor import IngredientProcessor
from services.regulatory.analyzer import RegulatoryAnalyzer
from utils.bedrock.client import BedrockClient

# Initialize clients
ingredient_processor = IngredientProcessor()
regulatory_analyzer = RegulatoryAnalyzer()
bedrock_client = BedrockClient()
textract_client = boto3.client('textract')
s3_client = boto3.client('s3')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Web API handler for image analysis requests
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    print(f"Received web API event: {json.dumps(event, default=str)}")
    
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
        'Content-Type': 'application/json'
    }
    
    # Handle preflight OPTIONS request
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'CORS preflight'})
        }
    
    # Handle GET request - return API info
    if event.get('httpMethod') == 'GET':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'service': 'Sookshma AI Web API',
                'version': '1.0.0',
                'endpoints': {
                    'POST /analyze': 'Analyze food label image',
                    'GET /health': 'Health check'
                }
            })
        }
    
    # Handle POST request - analyze image
    if event.get('httpMethod') == 'POST':
        return handle_image_analysis(event, context, headers)
    
    return {
        'statusCode': 405,
        'headers': headers,
        'body': json.dumps({'error': 'Method not allowed'})
    }

def handle_image_analysis(event: Dict[str, Any], context: Any, headers: Dict[str, str]) -> Dict[str, Any]:
    """Handle image analysis request"""
    
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        if 'image' not in body:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Missing image data'})
            }
        
        # Decode base64 image
        try:
            image_data = base64.b64decode(body['image'])
        except Exception as e:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Invalid base64 image data'})
            }
        
        # Save image to S3 for Textract processing
        bucket = os.getenv('IMAGE_BUCKET')
        key = f"web-uploads/{context.aws_request_id}.jpg"
        
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=image_data,
            ContentType='image/jpeg'
        )
        
        # Run OCR with Textract
        textract_response = textract_client.detect_document_text(
            Document={'S3Object': {'Bucket': bucket, 'Name': key}}
        )
        
        # Extract text from Textract response
        ocr_text = extract_text_from_textract(textract_response)
        
        if not ocr_text:
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'regulated_ingredients': [],
                    'non_regulated_ingredients': [],
                    'message': 'No text found in image. Please try a clearer photo of the ingredients list.'
                })
            }
        
        # Extract ingredients
        ingredients = ingredient_processor.extract_ingredients_from_text(ocr_text)
        
        if not ingredients:
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'regulated_ingredients': [],
                    'non_regulated_ingredients': [],
                    'message': 'No ingredients identified. Please ensure the image shows a clear ingredients list.'
                })
            }
        
        # Process ingredients and get regulatory data
        # Important: scan all extracted ingredients because regulated additives
        # often appear later in the list (not necessarily in the first 5).
        regulated_ingredients = []
        non_regulated_ingredients = []
        seen_ingredient_ids = set()

        for ingredient in ingredients:
            # Normalize ingredient name
            normalized = ingredient_processor.normalize_ingredient_name(ingredient)

            # Primary lookup by E-number when available
            regulatory_data = None
            if normalized.get('e_number'):
                regulatory_data = regulatory_analyzer.get_ingredient_regulatory_data(normalized['e_number'])

            # Fallback lookup by name only for low-confidence OCR variants.
            # This avoids false positives for regular ingredients like "wheat flour".
            if not regulatory_data and normalized.get('confidence') == 'low':
                search_results = regulatory_analyzer.search_ingredients_by_name(normalized.get('normalized', ingredient))
                if search_results:
                    regulatory_data = search_results[0]

            if not regulatory_data:
                non_regulated_ingredients.append({
                    'name': ingredient,
                    'normalized': normalized.get('normalized', ingredient)
                })
                continue

            ingredient_id = regulatory_data.get('ingredient_id')
            if ingredient_id in seen_ingredient_ids:
                continue
            seen_ingredient_ids.add(ingredient_id)

            # Get comparison
            comparison = regulatory_analyzer.get_regulatory_comparison(regulatory_data)

            # Generate AI explanation
            try:
                explanation = bedrock_client.generate_regulatory_explanation(
                    f"{regulatory_data['standard_name']} ({regulatory_data.get('ingredient_id', normalized.get('e_number', 'N/A'))})",
                    comparison
                )
            except Exception as e:
                print(f"Error generating explanation: {e}")
                explanation = f"Regulatory data available for {regulatory_data['standard_name']}. Check individual jurisdiction details for specific requirements."

            health_context = comparison.get('health_context', '')
            if health_context and health_context not in explanation:
                explanation = f"{explanation.strip()}\n\nRegulatory health-impact context: {health_context}"

            regulated_ingredients.append({
                'name': regulatory_data['standard_name'],
                'e_number': regulatory_data.get('ingredient_id', normalized.get('e_number')),
                'original_ingredient': ingredient,
                'jurisdictions': comparison['jurisdictions'],
                'explanation': explanation.strip()
            })
        
        # Clean up S3 object
        try:
            s3_client.delete_object(Bucket=bucket, Key=key)
        except:
            pass  # Don't fail if cleanup fails
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'regulated_ingredients': regulated_ingredients,
                'non_regulated_ingredients': non_regulated_ingredients,
                'ocr_text': ocr_text[:500] + '...' if len(ocr_text) > 500 else ocr_text,
                'total_ingredients_found': len(ingredients),
                'regulated_count': len(regulated_ingredients),
                'non_regulated_count': len(non_regulated_ingredients)
            })
        }
        
    except Exception as e:
        print(f"Error processing image analysis: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': 'Failed to process image. Please try again.'
            })
        }

def extract_text_from_textract(response: Dict[str, Any]) -> str:
    """Extract text from Textract response"""
    blocks = response.get('Blocks', [])
    text_lines = []
    
    for block in blocks:
        if block['BlockType'] == 'LINE':
            text_lines.append(block.get('Text', ''))
    
    return '\n'.join(text_lines)