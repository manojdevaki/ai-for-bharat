"""DynamoDB client utilities"""
import os
import boto3
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

class DynamoDBClient:
    """Client for DynamoDB operations"""
    
    def __init__(self):
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.regulatory_table = os.getenv('REGULATORY_DATA_TABLE', 'sookshma-regulatory-data')
        self.session_table = os.getenv('SESSION_TABLE', 'sookshma-sessions')
        self.dynamodb = boto3.resource('dynamodb', region_name=self.region)
    
    def get_ingredient_regulatory_data(self, ingredient_id: str) -> Optional[Dict[str, Any]]:
        """
        Get regulatory data for an ingredient
        
        Args:
            ingredient_id: Standardized ingredient identifier
            
        Returns:
            Regulatory data or None if not found
        """
        try:
            table = self.dynamodb.Table(self.regulatory_table)
            response = table.get_item(Key={'ingredient_id': ingredient_id})
            return response.get('Item')
        except Exception as e:
            print(f"Error fetching regulatory data: {e}")
            return None
    
    def query_ingredients_by_name(self, name: str) -> List[Dict[str, Any]]:
        """
        Query ingredients by name (for fuzzy matching)
        
        Args:
            name: Ingredient name to search
            
        Returns:
            List of matching ingredients
        """
        try:
            table = self.dynamodb.Table(self.regulatory_table)
            # This would use a GSI on ingredient names in production
            response = table.scan(
                FilterExpression='contains(search_names, :name)',
                ExpressionAttributeValues={':name': name.lower()}
            )
            return response.get('Items', [])
        except Exception as e:
            print(f"Error querying ingredients: {e}")
            return []
    
    def save_session(self, user_id: str, session_data: Dict[str, Any]) -> bool:
        """
        Save user session data
        
        Args:
            user_id: WhatsApp user ID
            session_data: Session information
            
        Returns:
            Success status
        """
        try:
            table = self.dynamodb.Table(self.session_table)
            
            # Add TTL (expire after 24 hours)
            ttl = int((datetime.now() + timedelta(hours=24)).timestamp())
            
            item = {
                'user_id': user_id,
                'session_data': session_data,
                'updated_at': datetime.now().isoformat(),
                'ttl': ttl
            }
            
            table.put_item(Item=item)
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def get_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user session data
        
        Args:
            user_id: WhatsApp user ID
            
        Returns:
            Session data or None
        """
        try:
            table = self.dynamodb.Table(self.session_table)
            response = table.get_item(Key={'user_id': user_id})
            return response.get('Item', {}).get('session_data')
        except Exception as e:
            print(f"Error fetching session: {e}")
            return None
    
    def batch_get_regulatory_data(self, ingredient_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Batch get regulatory data for multiple ingredients
        
        Args:
            ingredient_ids: List of ingredient identifiers
            
        Returns:
            List of regulatory data
        """
        try:
            table = self.dynamodb.Table(self.regulatory_table)
            
            keys = [{'ingredient_id': ing_id} for ing_id in ingredient_ids]
            response = self.dynamodb.batch_get_item(
                RequestItems={
                    self.regulatory_table: {'Keys': keys}
                }
            )
            
            return response.get('Responses', {}).get(self.regulatory_table, [])
        except Exception as e:
            print(f"Error batch fetching regulatory data: {e}")
            return []
