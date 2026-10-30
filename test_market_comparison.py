"""Offline unit tests. Run: python -m unittest test_market_comparison.py"""
import unittest
import pandas as pd
from market_comparison import match_products


def item(name, price, kg, store='shop', gtin=None):
    return {'name': name, 'price': price, 'weight_kg': kg,
            'currency': 'EUR', 'availability': 'https://schema.org/InStock',
            'store': store, 'url': 'https://example.org/p', 'gtin': gtin}


class ProductMatchingTests(unittest.TestCase):
    def test_exact_same_product(self):
        a = pd.DataFrame([item('Royal Canin Fit 32 2kg', 20, 2, 'a')])
        b = pd.DataFrame([item('Royal Canin Fit 32, 2 kg', 24, 2, 'b')])
        matched = match_products(a, b)
        self.assertEqual(len(matched), 1)
        self.assertEqual(matched.iloc[0]['difference_eur'], 4)
        self.assertEqual(matched.iloc[0]['difference_pct_vs_b'], 16.67)

    def test_different_weight_is_not_match(self):
        a = pd.DataFrame([item('Royal Canin Fit 32 2kg', 20, 2)])
        b = pd.DataFrame([item('Royal Canin Fit 32 4kg', 30, 4)])
        self.assertTrue(match_products(a, b).empty)

    def test_different_product_is_not_match(self):
        a = pd.DataFrame([item('Royal Canin Fit 32 2kg', 20, 2)])
        b = pd.DataFrame([item('Royal Canin Sterilised 2kg', 24, 2)])
        self.assertTrue(match_products(a, b).empty)

    def test_gtin_match(self):
        a = pd.DataFrame([item('A local product name', 20, 2, gtin='0000000123456')])
        b = pd.DataFrame([item('Other-language name', 24, 2, gtin='0000000123456')])
        self.assertEqual(len(match_products(a, b)), 1)

    def test_conflicting_gtin_not_match(self):
        a = pd.DataFrame([item('Royal Canin Fit 32 2kg', 20, 2, gtin='0000000123456')])
        b = pd.DataFrame([item('Royal Canin Fit 32 2kg', 24, 2, gtin='0000000123457')])
        self.assertTrue(match_products(a, b).empty)


if __name__ == '__main__':
    unittest.main()
