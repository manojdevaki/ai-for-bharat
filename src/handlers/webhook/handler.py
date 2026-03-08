"""WhatsApp webhook Lambda handler"""
import json
import os
import boto3
from typing import Dict, Any

# Import services
import sys
sys.path.append('/opt/python')  # Lambda layer path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from services.whatsapp.client import WhatsAppClient
from services.ingredient.processor import IngredientProcessor
from services.regulatory.analyzer import RegulatoryAnalyzer
from utils.bedrock.client import BedrockClient
from utils.dynamodb.client import DynamoDBClient

# Initialize clients
whatsapp_client = WhatsAppClient()
ingredient_processor = IngredientProcessor()
regulatory_analyzer = RegulatoryAnalyzer()
bedrock_client = BedrockClient()
dynamodb_client = DynamoDBClient()
textract_client = boto3.client('textract')
s3_client = boto3.client('s3')

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main webhook handler for WhatsApp messages
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    print(f"Received event: {json.dumps(event)}")
    
    # Handle webhook verification
    if event.get('httpMethod') == 'GET':
        return handle_verification(event)
    
    # Handle incoming messages
    if event.get('httpMethod') == 'POST':
        return handle_message(event)
    
    return {
        'statusCode': 400,
        'body': json.dumps({'error': 'Invalid request method'})
    }

def handle_verification(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle webhook verification"""
    params = event.get('queryStringParameters') or {}
    mode = params.get('hub.mode')
    token = params.get('hub.verify_token')
    challenge = params.get('hub.challenge')
    
    verified_challenge = whatsapp_client.verify_webhook(mode, token, challenge)
    
    if verified_challenge:
        return {
            'statusCode': 200,
            'body': verified_challenge
        }
    
    return {
        'statusCode': 403,
        'body': json.dumps({'error': 'Verification failed'})
    }

def handle_message(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle incoming WhatsApp message"""
    try:
        body = json.loads(event.get('body', '{}'))
        
        # Parse message
        message_data = whatsapp_client.parse_webhook_message(body)
        
        if not message_data:
            return {
                'statusCode': 200,
                'body': json.dumps({'status': 'no_message'})
            }
        
        # Mark message as read
        whatsapp_client.mark_message_read(message_data['message_id'])
        
        # Process based on message type
        if message_data['type'] == 'image':
            process_image_message(message_data)
        elif message_data['type'] == 'text':
            process_text_message(message_data)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'processed'})
        }
        
    except Exception as e:
        print(f"Error handling message: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def process_image_message(message_data: Dict[str, Any]):
    """Process food label image"""
    user_id = message_data['from']
    image_data = message_data['image']
    
    try:
        # Send acknowledgment
        whatsapp_client.send_message(
            user_id,
            "📸 Analyzing your food label... This will take a few seconds."
        )
        
        # Download image
        media_id = image_data.get('id')
        image_bytes = whatsapp_client.download_media(media_id)
        
        if not image_bytes:
            whatsapp_client.send_message(
                user_id,
                "❌ Sorry, I couldn't download the image. Please try again."
            )
            return
        
        # Save to S3
        bucket = os.getenv('IMAGE_BUCKET')
        key = f"uploads/{user_id}/{message_data['message_id']}.jpg"
        s3_client.put_object(Bucket=bucket, Key=key, Body=image_bytes)
        
        # Run OCR with Textract
        textract_response = textract_client.detect_document_text(
            Document={'S3Object': {'Bucket': bucket, 'Name': key}}
        )
        
        # Extract text from Textract response
        ocr_text = extract_text_from_textract(textract_response)
        
        if not ocr_text:
            whatsapp_client.send_message(
                user_id,
                "❌ I couldn't read any text from the image. Please ensure the label is clear and well-lit."
            )
            return
        
        # Extract ingredients using the new processor
        ingredients = ingredient_processor.extract_ingredients_from_text(ocr_text)
        
        if not ingredients:
            whatsapp_client.send_message(
                user_id,
                "❌ I couldn't identify any ingredients from the label. Please try a clearer image."
            )
            return
        
        # Process each ingredient
        analysis_results = []
        for ingredient in ingredients[:5]:  # Limit to first 5 for MVP
            # Normalize ingredient name
            normalized = ingredient_processor.normalize_ingredient_name(ingredient)
            
            # Get regulatory data
            regulatory_data = None
            if normalized['e_number']:
                regulatory_data = regulatory_analyzer.get_ingredient_regulatory_data(normalized['e_number'])
            
            if not regulatory_data and normalized['confidence'] == 'low':
                # Try searching by name
                search_results = regulatory_analyzer.search_ingredients_by_name(normalized['normalized'])
                if search_results:
                    regulatory_data = search_results[0]  # Take the first match
            
            if regulatory_data:
                # Generate comparison analysis
                comparison = regulatory_analyzer.get_regulatory_comparison(regulatory_data)
                
                # Generate explanation using Bedrock
                explanation = bedrock_client.generate_regulatory_explanation(
                    ingredient,
                    comparison
                )
                analysis_results.append({
                    'ingredient': ingredient,
                    'normalized': normalized,
                    'regulatory_data': regulatory_data,
                    'comparison': comparison,
                    'explanation': explanation
                })
            else:
                # No regulatory data found
                analysis_results.append({
                    'ingredient': ingredient,
                    'normalized': normalized,
                    'regulatory_data': None,
                    'comparison': None,
                    'explanation': f"No regulatory data found for {ingredient}. This may be a basic ingredient or not commonly regulated."
                })
        
        # Format and send response
        response_message = format_analysis_response(ingredients, analysis_results)
        whatsapp_client.send_message(user_id, response_message)
        
        # Save session for follow-up questions
        dynamodb_client.save_session(user_id, {
            'last_analysis': analysis_results,
            'ingredients': ingredients,
            'timestamp': message_data['timestamp']
        })
        
    except Exception as e:
        print(f"Error processing image: {e}")
        whatsapp_client.send_message(
            user_id,
            "❌ An error occurred while analyzing your image. Please try again."
        )

def process_text_message(message_data: Dict[str, Any]):
    """Process text message (follow-up questions)"""
    user_id = message_data['from']
    text = message_data['text']
    
    # Get session context
    session = dynamodb_client.get_session(user_id)
    
    if not session:
        # No context, send welcome message
        welcome_msg = """👋 Welcome to Sookshma AI!

I help you understand how the world regulates what India consumes.

📸 Send me a photo of any food label, and I'll analyze the ingredients and compare their regulatory status across India (FSSAI), EU, and US.

⚠️ Disclaimer: I provide regulatory information only, not medical advice."""
        whatsapp_client.send_message(user_id, welcome_msg)
        return
    
    # Handle follow-up question with context
    try:
        # Use Bedrock to answer with context
        context = json.dumps(session.get('last_analysis', []))
        
        system_prompt = f"""You are answering a follow-up question about food ingredients.
Previous analysis context: {context}

Provide factual regulatory information only. Do not give medical advice."""
        
        answer = bedrock_client.invoke_claude(text, system_prompt, max_tokens=1000)
        
        whatsapp_client.send_message(user_id, answer)
        
    except Exception as e:
        print(f"Error processing text message: {e}")
        whatsapp_client.send_message(
            user_id,
            "❌ Sorry, I couldn't process your question. Please try again."
        )

def extract_text_from_textract(response: Dict[str, Any]) -> str:
    """Extract text from Textract response"""
    blocks = response.get('Blocks', [])
    text_lines = []
    
    for block in blocks:
        if block['BlockType'] == 'LINE':
            text_lines.append(block.get('Text', ''))
    
    return '\n'.join(text_lines)


def format_analysis_response(ingredients: list, analysis_results: list) -> str:
    """Format the analysis response for WhatsApp"""
    
    message = f"""✅ Analysis Complete!

Found {len(ingredients)} ingredients in your product.

🔍 Regulatory Analysis:

"""
    
    for result in analysis_results:
        ingredient_name = result['ingredient']
        normalized = result['normalized']
        explanation = result['explanation']
        
        # Add confidence indicator
        confidence_emoji = "🎯" if normalized['confidence'] == 'high' else "🔍" if normalized['confidence'] == 'medium' else "❓"
        
        message += f"{confidence_emoji} **{ingredient_name}**"
        
        if normalized['e_number']:
            message += f" ({normalized['e_number']})"
        
        message += f":\n{explanation}\n\n"
        message += "---\n"
    
    message += """\n
ℹ️ **DISCLAIMER**: This is regulatory information only, not medical advice. Regulatory status does not equal safety recommendations. Please consult healthcare professionals for personalized guidance.

💬 Have questions about any ingredient? Just ask!"""
    
    return message
