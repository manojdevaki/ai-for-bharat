"""Ingredient processing and normalization service"""
import re
from typing import List, Dict, Any, Optional
from difflib import SequenceMatcher

class IngredientProcessor:
    """Service for processing and normalizing ingredient names"""
    
    def __init__(self):
        # Common ingredient name variations and mappings
        self.common_mappings = {
            # E-numbers with common names
            'tartrazine': 'E102',
            'yellow 5': 'E102',
            'fd&c yellow no. 5': 'E102',
            'sunset yellow': 'E110',
            'yellow 6': 'E110',
            'fd&c yellow no. 6': 'E110',
            'msg': 'E621',
            'monosodium glutamate': 'E621',
            'ajinomoto': 'E621',
            'sodium benzoate': 'E211',
            'potassium sorbate': 'E202',
            'ascorbic acid': 'E300',
            'vitamin c': 'E300',
            'citric acid': 'E330',
            'lecithin': 'E322',
            'bha': 'E320',
            'butylated hydroxyanisole': 'E320',
            'bht': 'E321',
            'butylated hydroxytoluene': 'E321',
            'carmine': 'E120',
            'cochineal': 'E120',
            'annatto': 'E160b',
            'beta carotene': 'E160a',
            'caramel': 'E150a',
            'titanium dioxide': 'E171',
            'iron oxide': 'E172',
            'calcium carbonate': 'E170',
            'sodium nitrite': 'E250',
            'sodium nitrate': 'E251',
            'potassium nitrite': 'E249',
            'potassium nitrate': 'E252',
            'sulfur dioxide': 'E220',
            'sodium sulfite': 'E221',
            'sodium metabisulfite': 'E223',
            'potassium metabisulfite': 'E224'
        }
        
        # Hindi to English mappings for common ingredients
        self.hindi_mappings = {
            'नमक': 'salt',
            'चीनी': 'sugar',
            'तेल': 'oil',
            'मसाला': 'spice',
            'हल्दी': 'turmeric',
            'धनिया': 'coriander',
            'जीरा': 'cumin',
            'लाल मिर्च': 'red chili',
            'काली मिर्च': 'black pepper',
            'अदरक': 'ginger',
            'लहसुन': 'garlic',
            'प्याज': 'onion'
        }
    
    def extract_ingredients_from_text(self, text: str) -> List[str]:
        """
        Extract ingredient names from OCR text
        
        Args:
            text: Raw OCR text from food label
            
        Returns:
            List of extracted ingredient names
        """
        # Clean the text
        cleaned_text = self._clean_text(text)
        
        # Look for ingredients section
        ingredients_section = self._find_ingredients_section(cleaned_text)
        
        if not ingredients_section:
            # Fallback: try to extract from entire text
            ingredients_section = cleaned_text
        
        # Extract individual ingredients
        ingredients = self._parse_ingredients_list(ingredients_section)
        
        # Clean and normalize ingredient names
        cleaned_ingredients = []
        for ingredient in ingredients:
            cleaned = self._clean_ingredient_name(ingredient)
            if cleaned and len(cleaned) > 2:  # Filter out very short strings
                cleaned_ingredients.append(cleaned)
        
        # Add explicit additive codes found in text (e.g., E500ii, 500(ii), 322)
        additive_codes = self._extract_additive_codes(ingredients_section)
        for code in additive_codes:
            if code not in cleaned_ingredients:
                cleaned_ingredients.append(code)

        return cleaned_ingredients[:20]  # Limit to first 20 ingredients
    
    def normalize_ingredient_name(self, ingredient: str) -> Dict[str, Any]:
        """
        Normalize ingredient name to standard format
        
        Args:
            ingredient: Raw ingredient name
            
        Returns:
            Dictionary with normalized ingredient information
        """
        # Clean the ingredient name
        cleaned = self._clean_ingredient_name(ingredient)
        
        # Check for direct E-number
        e_number = self._extract_e_number(cleaned)
        if e_number:
            return {
                'original': ingredient,
                'normalized': e_number,
                'e_number': e_number,
                'confidence': 'high',
                'match_type': 'e_number'
            }
        
        # Check common mappings
        lower_cleaned = cleaned.lower()
        if lower_cleaned in self.common_mappings:
            e_number = self.common_mappings[lower_cleaned]
            return {
                'original': ingredient,
                'normalized': e_number,
                'e_number': e_number,
                'confidence': 'high',
                'match_type': 'common_name'
            }
        
        # Check Hindi mappings
        if cleaned in self.hindi_mappings:
            english_name = self.hindi_mappings[cleaned]
            return {
                'original': ingredient,
                'normalized': english_name,
                'e_number': None,
                'confidence': 'medium',
                'match_type': 'hindi_translation'
            }
        
        # Try fuzzy matching with common names
        best_match = self._fuzzy_match_ingredient(lower_cleaned)
        if best_match:
            return {
                'original': ingredient,
                'normalized': best_match['e_number'],
                'e_number': best_match['e_number'],
                'confidence': 'medium' if best_match['score'] > 0.8 else 'low',
                'match_type': 'fuzzy_match'
            }
        
        # Return as-is if no match found
        return {
            'original': ingredient,
            'normalized': cleaned,
            'e_number': None,
            'confidence': 'low',
            'match_type': 'no_match'
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean OCR text"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common OCR artifacts
        cleaned = re.sub(r'[|\\/_]+', ' ', cleaned)
        
        return cleaned
    
    def _find_ingredients_section(self, text: str) -> Optional[str]:
        """Find the ingredients section in the text"""
        # Common patterns for ingredients section
        patterns = [
            r'ingredients?\s*[:]\s*(.+?)(?:nutrition|allergen|contains|net|weight|best|exp|mfg|$)',
            r'ingredients?\s*[-]\s*(.+?)(?:nutrition|allergen|contains|net|weight|best|exp|mfg|$)',
            r'ingredients?\s*\n(.+?)(?:nutrition|allergen|contains|net|weight|best|exp|mfg|$)',
            r'सामग्री\s*[:]\s*(.+?)(?:पोषण|एलर्जी|शामिल|नेट|वजन|सर्वोत्तम|$)',
        ]
        
        text_lower = text.lower()
        
        for pattern in patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _parse_ingredients_list(self, text: str) -> List[str]:
        """Parse ingredients from text"""
        if not text:
            return []
        
        # Split by common delimiters
        ingredients = []
        
        # Try comma separation first
        parts = re.split(r'[,;]', text)
        
        if len(parts) > 1:
            ingredients = parts
        else:
            # Try other separators
            parts = re.split(r'[\n\r]+', text)
            if len(parts) > 1:
                ingredients = parts
            else:
                # Split by periods or other punctuation
                parts = re.split(r'[.•·]', text)
                ingredients = parts
        
        return [ing.strip() for ing in ingredients if ing.strip()]
    
    def _clean_ingredient_name(self, ingredient: str) -> str:
        """Clean individual ingredient name"""
        if not ingredient:
            return ""
        
        # Remove brackets and parentheses content
        cleaned = re.sub(r'\([^)]*\)', '', ingredient)
        cleaned = re.sub(r'\[[^\]]*\]', '', cleaned)
        
        # Remove numbers at the beginning (like "1. Salt")
        cleaned = re.sub(r'^\d+\.?\s*', '', cleaned)
        
        # Remove special characters but keep letters, numbers, spaces, and hyphens
        cleaned = re.sub(r'[^\w\s\-&]', '', cleaned)
        
        # Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned.strip())
        
        return cleaned
    
    def _extract_e_number(self, text: str) -> Optional[str]:
        """Extract E-number from text"""
        # Pattern for E-numbers (E followed by 3-4 digits, optionally followed by letters like 'ii', 'a', etc.)
        pattern = r'\bE\s*(\d{3,4}[a-z]*)\b'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            return f"E{match.group(1)}"

        # Support India-style additive notation without explicit 'E', e.g. 500(ii), 503ii, 322
        # 1) Code with parenthesized suffix: 500(ii)
        paren_pattern = r'\b(\d{3,4})\s*\(\s*([ivx]+|[a-z]{1,3})\s*\)\b'
        paren_match = re.search(paren_pattern, text, re.IGNORECASE)
        if paren_match:
            return f"E{paren_match.group(1)}{paren_match.group(2).lower()}"

        # 2) Plain numeric additive code in common range, e.g. 322
        numeric_pattern = r'^\s*(\d{3,4})\s*$'
        numeric_match = re.search(numeric_pattern, text)
        if numeric_match:
            code = int(numeric_match.group(1))
            if 100 <= code <= 1599:
                return f"E{numeric_match.group(1)}"
        
        return None

    def _extract_additive_codes(self, text: str) -> List[str]:
        """Extract additive codes from free text and normalize to E-numbers."""
        if not text:
            return []

        found_codes: List[str] = []

        # 1) Explicit E-number style: E500ii
        for match in re.findall(r'\bE\s*(\d{3,4}[a-z]*)\b', text, re.IGNORECASE):
            code = f"E{match.lower()}"
            if code not in found_codes:
                found_codes.append(code)

        # 2) INS style with suffix in parentheses: 500(ii), 503(II)
        for base, suffix in re.findall(r'\b(\d{3,4})\s*\(\s*([ivx]+|[a-z]{1,3})\s*\)', text, re.IGNORECASE):
            code = f"E{base}{suffix.lower()}"
            if code not in found_codes:
                found_codes.append(code)

        # 3) Parenthesized plain numeric codes after additive-class keywords: Emulsifier (322)
        keyword_pattern = (
            r'(?:emulsifier|leavening\s+agents?|raising\s+agents?|preservative|acidity\s+regulator|'
            r'colour|color|stabilizer|antioxidant)\s*[:\-]?\s*\((\d{3,4})\)'
        )
        for base in re.findall(keyword_pattern, text, re.IGNORECASE):
            code = f"E{base}"
            if code not in found_codes:
                found_codes.append(code)

        return found_codes
    
    def _fuzzy_match_ingredient(self, ingredient: str) -> Optional[Dict[str, Any]]:
        """Fuzzy match ingredient name with known mappings"""
        best_score = 0
        best_match = None
        
        for known_name, e_number in self.common_mappings.items():
            score = SequenceMatcher(None, ingredient, known_name).ratio()
            if score > best_score and score > 0.7:  # Minimum threshold
                best_score = score
                best_match = {
                    'e_number': e_number,
                    'matched_name': known_name,
                    'score': score
                }
        
        return best_match
    
    def get_ingredient_variations(self, e_number: str) -> List[str]:
        """Get common variations of an ingredient name"""
        variations = []
        
        # Find all names that map to this E-number
        for name, mapped_e_number in self.common_mappings.items():
            if mapped_e_number == e_number:
                variations.append(name)
        
        return variations