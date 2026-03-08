#!/usr/bin/env python3
"""
Unit tests for Regulatory Analyzer
"""

import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.regulatory.analyzer import RegulatoryAnalyzer

class TestRegulatoryAnalyzer(unittest.TestCase):
    
    def setUp(self):
        self.analyzer = RegulatoryAnalyzer()
    
    def test_get_ingredient_regulatory_data(self):
        """Test regulatory data retrieval"""
        
        # Test known ingredient
        data_e102 = self.analyzer.get_ingredient_regulatory_data('E102')
        self.assertIsNotNone(data_e102)
        self.assertEqual(data_e102['ingredient_id'], 'E102')
        self.assertIn('name', data_e102)
        self.assertIn('regulatory_status', data_e102)
        
        # Test unknown ingredient
        data_unknown = self.analyzer.get_ingredient_regulatory_data('E999')
        self.assertIsNone(data_unknown)
    
    def test_get_regulatory_comparison(self):
        """Test regulatory comparison logic"""
        
        # Get sample data
        data_e102 = self.analyzer.get_ingredient_regulatory_data('E102')
        if data_e102:
            comparison = self.analyzer.get_regulatory_comparison(data_e102)
            
            self.assertIn('summary', comparison)
            self.assertIn('details', comparison)
            self.assertIn('jurisdictions', comparison)
            
            # Check jurisdictions
            jurisdictions = comparison['jurisdictions']
            self.assertIn('india', jurisdictions)
            self.assertIn('eu', jurisdictions)
            self.assertIn('us', jurisdictions)
    
    def test_search_ingredients_by_name(self):
        """Test ingredient search functionality"""
        
        # Search for common ingredient
        results = self.analyzer.search_ingredients_by_name('tartrazine')
        self.assertGreater(len(results), 0)
        
        # Search should be case-insensitive
        results_upper = self.analyzer.search_ingredients_by_name('TARTRAZINE')
        self.assertEqual(len(results), len(results_upper))
        
        # Search for non-existent ingredient
        results_none = self.analyzer.search_ingredients_by_name('nonexistentingredient123')
        self.assertEqual(len(results_none), 0)
    
    def test_regulatory_status_logic(self):
        """Test regulatory status determination logic"""
        
        # Test various regulatory scenarios
        test_cases = [
            {
                'india': {'status': 'approved', 'restrictions': None},
                'eu': {'status': 'approved', 'restrictions': 'warning_label'},
                'us': {'status': 'approved', 'restrictions': None},
                'expected_summary': 'approved in all major jurisdictions'
            },
            {
                'india': {'status': 'approved', 'restrictions': None},
                'eu': {'status': 'banned', 'restrictions': None},
                'us': {'status': 'approved', 'restrictions': None},
                'expected_contains': 'mixed regulatory status'
            }
        ]
        
        for case in test_cases:
            mock_data = {
                'ingredient_id': 'TEST',
                'name': 'Test Ingredient',
                'regulatory_status': {
                    'india': case['india'],
                    'eu': case['eu'],
                    'us': case['us']
                }
            }
            
            comparison = self.analyzer.get_regulatory_comparison(mock_data)
            
            if 'expected_summary' in case:
                self.assertIn(case['expected_summary'], comparison['summary'].lower())
            if 'expected_contains' in case:
                self.assertIn(case['expected_contains'], comparison['summary'].lower())

if __name__ == '__main__':
    unittest.main()