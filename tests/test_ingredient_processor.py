#!/usr/bin/env python3
"""
Unit tests for Ingredient Processor
"""

import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.ingredient.processor import IngredientProcessor

class TestIngredientProcessor(unittest.TestCase):
    
    def setUp(self):
        self.processor = IngredientProcessor()
    
    def test_extract_ingredients_from_text(self):
        """Test ingredient extraction from OCR text"""
        
        # Test case 1: Simple ingredient list
        text1 = "Ingredients: Water, Sugar, Tartrazine (E102), Sodium Benzoate (E211)"
        ingredients1 = self.processor.extract_ingredients_from_text(text1)
        
        self.assertIn('water', [i.lower() for i in ingredients1])
        self.assertIn('sugar', [i.lower() for i in ingredients1])
        self.assertIn('tartrazine', [i.lower() for i in ingredients1])
        self.assertIn('sodium benzoate', [i.lower() for i in ingredients1])
        
        # Test case 2: Mixed Hindi-English
        text2 = "सामग्री: पानी, चीनी, Tartrazine, MSG"
        ingredients2 = self.processor.extract_ingredients_from_text(text2)
        
        self.assertGreater(len(ingredients2), 0)
        
        # Test case 3: E-numbers
        text3 = "Contains: E102, E211, E621"
        ingredients3 = self.processor.extract_ingredients_from_text(text3)
        
        self.assertIn('E102', ingredients3)
        self.assertIn('E211', ingredients3)
        self.assertIn('E621', ingredients3)
    
    def test_normalize_ingredient_name(self):
        """Test ingredient name normalization"""
        
        # Test E-number recognition
        result1 = self.processor.normalize_ingredient_name("Tartrazine")
        self.assertEqual(result1['e_number'], 'E102')
        self.assertEqual(result1['confidence'], 'high')
        
        # Test direct E-number
        result2 = self.processor.normalize_ingredient_name("E102")
        self.assertEqual(result2['e_number'], 'E102')
        self.assertEqual(result2['confidence'], 'high')
        
        # Test MSG variants
        result3 = self.processor.normalize_ingredient_name("MSG")
        self.assertEqual(result3['e_number'], 'E621')
        
        result4 = self.processor.normalize_ingredient_name("Monosodium Glutamate")
        self.assertEqual(result4['e_number'], 'E621')
        
        # Test unknown ingredient
        result5 = self.processor.normalize_ingredient_name("Unknown Chemical")
        self.assertIsNone(result5['e_number'])
        self.assertEqual(result5['confidence'], 'low')
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        
        # Empty text
        ingredients_empty = self.processor.extract_ingredients_from_text("")
        self.assertEqual(len(ingredients_empty), 0)
        
        # No ingredients text
        ingredients_none = self.processor.extract_ingredients_from_text("This is just random text")
        self.assertEqual(len(ingredients_none), 0)
        
        # Very long ingredient list
        long_text = "Ingredients: " + ", ".join([f"Ingredient{i}" for i in range(100)])
        ingredients_long = self.processor.extract_ingredients_from_text(long_text)
        self.assertGreater(len(ingredients_long), 50)  # Should extract many ingredients

if __name__ == '__main__':
    unittest.main()