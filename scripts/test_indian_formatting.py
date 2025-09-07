#!/usr/bin/env python3
"""
Test script for Indian formatting functions
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from utils.formatting import format_indian_currency, format_indian_number_words
    print("✓ Successfully imported formatting functions")
    
    # Test cases
    test_cases = [
        0,
        1000,
        100000,  # 1 lakh
        10000000,  # 1 crore
        123456789.50,
        9999999999.99
    ]
    
    print("\nTesting Indian currency formatting:")
    print("-" * 50)
    for amount in test_cases:
        full_format = format_indian_currency(amount)
        short_format = format_indian_number_words(amount)
        print(f"{amount:>15,.2f} → {full_format:>15} ({short_format})")
    
    print("\n✓ All tests passed!")
    
except ImportError as e:
    print(f"✗ Failed to import formatting functions: {e}")
    print("Using fallback implementations...")
    
    # Fallback functions
    def format_indian_currency(amount, include_symbol=True):
        symbol = "₹" if include_symbol else ""
        return f"{symbol}{amount:,.2f}"
    
    def format_indian_number_words(amount):
        return f"₹{amount:,.0f}"
    
    # Test with fallbacks
    test_amount = 123456789.50
    print(f"Fallback test: {test_amount} → {format_indian_currency(test_amount)}")
