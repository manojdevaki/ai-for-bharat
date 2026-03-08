"""Regulatory analysis service"""
import re
from typing import Dict, Any, List, Optional
import boto3
from boto3.dynamodb.conditions import Key, Attr

class RegulatoryAnalyzer:
    """Service for analyzing regulatory data and generating comparisons"""
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        self.regulatory_table = self.dynamodb.Table('sookshma-regulatory-data')
    
    def get_ingredient_regulatory_data(self, ingredient_id: str) -> Optional[Dict[str, Any]]:
        """
        Get regulatory data for a specific ingredient
        
        Args:
            ingredient_id: E-number or ingredient identifier
            
        Returns:
            Regulatory data or None if not found
        """
        try:
            response = self.regulatory_table.get_item(Key={'ingredient_id': ingredient_id})
            return response.get('Item')
        except Exception as e:
            print(f"Error fetching regulatory data for {ingredient_id}: {e}")
            return None
    
    def search_ingredients_by_name(self, name: str) -> List[Dict[str, Any]]:
        """
        Search for ingredients by name using scan with filter
        
        Args:
            name: Ingredient name to search for
            
        Returns:
            List of matching ingredients
        """
        if not name:
            return []

        try:
            query = str(name).strip().lower()
            if not query:
                return []

            # Small MVP table size: full scan + case-insensitive in-memory match is
            # more reliable than case-sensitive DynamoDB contains filters.
            items: List[Dict[str, Any]] = []
            response = self.regulatory_table.scan()
            items.extend(response.get('Items', []))

            while 'LastEvaluatedKey' in response:
                response = self.regulatory_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response.get('Items', []))

            matches: List[Dict[str, Any]] = []
            for item in items:
                candidates: List[str] = [
                    str(item.get('standard_name', '')),
                    str(item.get('ingredient_id', '')),
                ]

                common_names = item.get('common_names', [])
                if isinstance(common_names, list):
                    candidates.extend([str(v) for v in common_names])
                elif common_names:
                    candidates.append(str(common_names))

                query_tokens = [t for t in re.findall(r'[a-z0-9]+', query) if len(t) > 2]

                for candidate in candidates:
                    candidate_lower = candidate.lower().strip()
                    if not candidate_lower:
                        continue

                    # Strong match 1: direct query contained in candidate text.
                    if len(query) >= 4 and query in candidate_lower:
                        matches.append(item)
                        break

                    # Strong match 2: significant token overlap.
                    candidate_tokens = {t for t in re.findall(r'[a-z0-9]+', candidate_lower) if len(t) > 2}
                    if not query_tokens or not candidate_tokens:
                        continue

                    overlap = len(set(query_tokens).intersection(candidate_tokens))
                    if overlap >= 2 and overlap / max(len(query_tokens), 1) >= 0.6:
                        matches.append(item)
                        break

            return matches
        except Exception as e:
            print(f"Error searching ingredients by name '{name}': {e}")
            return []
    
    def get_regulatory_comparison(self, ingredient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate regulatory comparison across jurisdictions
        
        Args:
            ingredient_data: Complete ingredient regulatory data
            
        Returns:
            Comparison analysis
        """
        if not ingredient_data:
            return {}
        
        comparison = {
            'ingredient_id': ingredient_data.get('ingredient_id'),
            'standard_name': ingredient_data.get('standard_name'),
            'category': ingredient_data.get('category'),
            'jurisdictions': {},
            'differences': [],
            'warnings': [],
            'summary': '',
            'health_context': ''
        }
        
        # Analyze each jurisdiction
        jurisdictions = ['india', 'eu', 'us']
        statuses = {}
        
        for jurisdiction in jurisdictions:
            if jurisdiction in ingredient_data:
                jurisdiction_data = ingredient_data[jurisdiction]
                comparison['jurisdictions'][jurisdiction] = {
                    'status': jurisdiction_data.get('status'),
                    'authority': jurisdiction_data.get('authority'),
                    'limits': jurisdiction_data.get('limits'),
                    'restrictions': jurisdiction_data.get('restrictions'),
                    'source': jurisdiction_data.get('source')
                }
                statuses[jurisdiction] = jurisdiction_data.get('status')
        
        # Identify differences
        comparison['differences'] = self._identify_differences(statuses)
        
        # Generate warnings
        comparison['warnings'] = self._generate_warnings(ingredient_data, statuses)
        
        # Generate summary
        comparison['summary'] = self._generate_summary(ingredient_data, statuses, comparison['differences'])

        # Generate regulatory health-impact context (non-medical)
        comparison['health_context'] = self._generate_health_context(ingredient_data, statuses)
        
        return comparison
    
    def batch_get_regulatory_data(self, ingredient_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get regulatory data for multiple ingredients
        
        Args:
            ingredient_ids: List of ingredient identifiers
            
        Returns:
            List of regulatory data
        """
        if not ingredient_ids:
            return []
        
        try:
            # DynamoDB batch_get_item has a limit of 100 items
            results = []
            
            for i in range(0, len(ingredient_ids), 100):
                batch = ingredient_ids[i:i+100]
                keys = [{'ingredient_id': ing_id} for ing_id in batch]
                
                response = self.dynamodb.batch_get_item(
                    RequestItems={
                        'sookshma-regulatory-data': {'Keys': keys}
                    }
                )
                
                batch_results = response.get('Responses', {}).get('sookshma-regulatory-data', [])
                results.extend(batch_results)
            
            return results
        except Exception as e:
            print(f"Error batch fetching regulatory data: {e}")
            return []
    
    def get_ingredients_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all ingredients in a specific category
        
        Args:
            category: Ingredient category (e.g., 'food_color', 'preservative')
            
        Returns:
            List of ingredients in the category
        """
        try:
            response = self.regulatory_table.scan(
                FilterExpression=Attr('category').eq(category)
            )
            return response.get('Items', [])
        except Exception as e:
            print(f"Error fetching ingredients by category '{category}': {e}")
            return []
    
    def _identify_differences(self, statuses: Dict[str, str]) -> List[str]:
        """Identify regulatory differences between jurisdictions"""
        differences = []
        
        # Check if all statuses are the same
        unique_statuses = set(statuses.values())
        
        if len(unique_statuses) > 1:
            # There are differences
            for jurisdiction, status in statuses.items():
                if status == 'banned':
                    differences.append(f"Banned in {jurisdiction.upper()}")
                elif status == 'approved_with_warning':
                    differences.append(f"Requires warning labels in {jurisdiction.upper()}")
                elif status == 'restricted':
                    differences.append(f"Restricted use in {jurisdiction.upper()}")
        
        return differences
    
    def _generate_warnings(self, ingredient_data: Dict[str, Any], statuses: Dict[str, str]) -> List[str]:
        """Generate warnings based on regulatory data"""
        warnings = []
        
        # Check for banned status
        for jurisdiction, status in statuses.items():
            if status == 'banned':
                warnings.append(f"⚠️ This ingredient is BANNED in {jurisdiction.upper()}")
        
        # Check for warning requirements
        for jurisdiction, status in statuses.items():
            if status == 'approved_with_warning':
                warnings.append(f"⚠️ Warning labels required in {jurisdiction.upper()}")
            elif status == 'not_listed':
                warnings.append(f"ℹ️ No direct listing found in {jurisdiction.upper()} official source set")
        
        # Check for specific notes
        notes = ingredient_data.get('notes', '')
        if 'cancer' in notes.lower():
            warnings.append("⚠️ Potential health concerns identified by some authorities")
        
        return warnings
    
    def _generate_summary(self, ingredient_data: Dict[str, Any], statuses: Dict[str, str], differences: List[str]) -> str:
        """Generate a summary of regulatory status"""
        name = ingredient_data.get('standard_name', 'Unknown ingredient')
        category = ingredient_data.get('category', 'unknown')
        
        # Count approvals
        approved_count = sum(1 for status in statuses.values() if status in ['approved', 'gras'])
        not_listed_count = sum(1 for status in statuses.values() if status == 'not_listed')
        total_jurisdictions = len(statuses)

        if not_listed_count > 0:
            return (
                f"{name} is approved in some jurisdictions, but at least one authority currently has no direct listing "
                "in the verified source set."
            )
        
        if approved_count == total_jurisdictions:
            if differences:
                return f"{name} is approved in all major jurisdictions but with different requirements."
            else:
                return f"{name} is approved in all major jurisdictions with similar requirements."
        elif approved_count == 0:
            return f"{name} has regulatory restrictions or is banned in all checked jurisdictions."
        else:
            return f"{name} has mixed regulatory status - approved in {approved_count} out of {total_jurisdictions} jurisdictions."

    def _generate_health_context(self, ingredient_data: Dict[str, Any], statuses: Dict[str, str]) -> str:
        """Generate concise, non-medical health-impact context from regulatory signals."""
        if not statuses:
            return ""

        name = ingredient_data.get('standard_name', 'This ingredient')
        banned_regions = [j.upper() for j, s in statuses.items() if s == 'banned']
        warning_regions = [j.upper() for j, s in statuses.items() if s == 'approved_with_warning']
        restricted_regions = [j.upper() for j, s in statuses.items() if s == 'restricted']
        not_listed_regions = [j.upper() for j, s in statuses.items() if s == 'not_listed']

        notes = (ingredient_data.get('notes') or '').lower()
        note_signal = ""
        if 'cancer' in notes or 'carcin' in notes:
            note_signal = "Some authorities mention potential long-term risk signals in available notes."
        elif 'hyperactivity' in notes:
            note_signal = "Some authorities mention behavioral sensitivity concerns for certain groups."

        if not_listed_regions:
            return (
                f"{name} has no direct listing identified in {', '.join(not_listed_regions)} official source data. "
                "This means the current dataset cannot confirm an explicit status for that jurisdiction and should be verified against the latest regulator publication."
            )

        if banned_regions:
            return (
                f"{name} is banned in {', '.join(banned_regions)}. "
                f"This usually indicates higher regulatory caution or unresolved safety concerns for some uses. "
                f"{note_signal}".strip()
            )

        if warning_regions or restricted_regions:
            parts = []
            if warning_regions:
                parts.append(f"warning-label requirements in {', '.join(warning_regions)}")
            if restricted_regions:
                parts.append(f"restricted-use limits in {', '.join(restricted_regions)}")
            joined = ' and '.join(parts)
            return (
                f"{name} has {joined}. "
                f"This suggests permitted use with additional risk-management controls by regulators. "
                f"{note_signal}".strip()
            )

        return (
            f"{name} is broadly permitted in listed jurisdictions at regulated limits. "
            "Regulatory limits are designed to control exposure under expected consumption patterns."
        )
    
    def get_similar_ingredients(self, ingredient_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get ingredients similar to the given one (same category)
        
        Args:
            ingredient_id: Reference ingredient ID
            limit: Maximum number of similar ingredients to return
            
        Returns:
            List of similar ingredients
        """
        try:
            # First get the reference ingredient
            reference = self.get_ingredient_regulatory_data(ingredient_id)
            if not reference:
                return []
            
            category = reference.get('category')
            if not category:
                return []
            
            # Get other ingredients in the same category
            similar = self.get_ingredients_by_category(category)
            
            # Remove the reference ingredient and limit results
            similar = [ing for ing in similar if ing.get('ingredient_id') != ingredient_id]
            
            return similar[:limit]
        except Exception as e:
            print(f"Error finding similar ingredients for {ingredient_id}: {e}")
            return []