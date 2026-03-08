"""WhatsApp Business API client"""
import os
import requests
from typing import Dict, Any, Optional

class WhatsAppClient:
    """Client for WhatsApp Business Cloud API"""
    
    def __init__(self):
        self.api_url = os.getenv('WHATSAPP_API_URL', 'https://graph.facebook.com/v18.0')
        self.phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
        self.access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
        self.verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN')
    
    def send_message(self, to: str, message: str) -> bool:
        """
        Send text message to WhatsApp user
        
        Args:
            to: Recipient phone number
            message: Message text
            
        Returns:
            Success status
        """
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': to,
            'type': 'text',
            'text': {'body': message}
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
            return False
    
    def mark_message_read(self, message_id: str) -> bool:
        """
        Mark message as read
        
        Args:
            message_id: WhatsApp message ID
            
        Returns:
            Success status
        """
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'messaging_product': 'whatsapp',
            'status': 'read',
            'message_id': message_id
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error marking message as read: {e}")
            return False
    
    def download_media(self, media_id: str) -> Optional[bytes]:
        """
        Download media file from WhatsApp
        
        Args:
            media_id: WhatsApp media ID
            
        Returns:
            Media file bytes or None
        """
        # First, get media URL
        url = f"{self.api_url}/{media_id}"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            media_url = response.json().get('url')
            
            if not media_url:
                return None
            
            # Download the actual media
            media_response = requests.get(media_url, headers=headers)
            media_response.raise_for_status()
            return media_response.content
            
        except Exception as e:
            print(f"Error downloading media: {e}")
            return None
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """
        Verify webhook subscription
        
        Args:
            mode: Verification mode
            token: Verification token
            challenge: Challenge string
            
        Returns:
            Challenge if verified, None otherwise
        """
        if mode == 'subscribe' and token == self.verify_token:
            return challenge
        return None
    
    def parse_webhook_message(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse incoming webhook message
        
        Args:
            payload: Webhook payload
            
        Returns:
            Parsed message data or None
        """
        try:
            entry = payload.get('entry', [])[0]
            changes = entry.get('changes', [])[0]
            value = changes.get('value', {})
            messages = value.get('messages', [])
            
            if not messages:
                return None
            
            message = messages[0]
            
            return {
                'message_id': message.get('id'),
                'from': message.get('from'),
                'timestamp': message.get('timestamp'),
                'type': message.get('type'),
                'text': message.get('text', {}).get('body'),
                'image': message.get('image'),
                'contacts': value.get('contacts', [])
            }
        except Exception as e:
            print(f"Error parsing webhook message: {e}")
            return None
