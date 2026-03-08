"""Static file handler for serving web interface from API Gateway"""
import json
import base64
import os
from typing import Dict, Any

# Version: 1.1 - Updated for JPEG conversion fix

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Static file handler for serving web interface files
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response with static file content
    """
    print(f"Static file request: {json.dumps(event, default=str)}")
    
    # Get the requested path
    path = event.get('path', '/')
    
    # Default to index.html for root path
    if path == '/' or path == '':
        path = '/index.html'
    
    # Remove leading slash
    if path.startswith('/'):
        path = path[1:]
    
    # Security: only allow specific files
    # Note: When deployed, Lambda runs from src/ directory
    allowed_files = {
        'index.html': ('text/html', 'web/index.html'),
        'sookshma-ai-logo.png': ('image/png', 'web/sookshma-ai-logo.png'),
        '': ('text/html', 'web/index.html')  # Default for empty path
    }
    
    if path not in allowed_files:
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache'
            },
            'body': '<html><body><h1>404 Not Found</h1></body></html>'
        }
    
    content_type, file_path = allowed_files[path]
    
    try:
        # Check if file exists and log the path
        print(f"Attempting to read file: {file_path}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"File exists: {os.path.exists(file_path)}")
        
        # List directory contents for debugging
        if os.path.exists('web'):
            print(f"Contents of web/: {os.listdir('web')}")
        
        # Read the file
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        print(f"Successfully read {len(file_content)} bytes from {file_path}")
        
        # For binary files (images), encode as base64
        if content_type.startswith('image/'):
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': content_type,
                    'Cache-Control': 'public, max-age=86400'
                },
                'body': base64.b64encode(file_content).decode('utf-8'),
                'isBase64Encoded': True
            }
        else:
            # For text files, return as string
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': content_type,
                    'Cache-Control': 'public, max-age=300'
                },
                'body': file_content.decode('utf-8')
            }
            
    except FileNotFoundError as e:
        print(f"File not found: {file_path}")
        print(f"Error: {e}")
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache'
            },
            'body': f'<html><body><h1>404 File Not Found</h1><p>Path: {file_path}</p></body></html>'
        }
    except Exception as e:
        print(f"Error serving static file: {e}")
        print(f"File path: {file_path}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache'
            },
            'body': f'<html><body><h1>500 Internal Server Error</h1><p>Error: {str(e)}</p></body></html>'
        }