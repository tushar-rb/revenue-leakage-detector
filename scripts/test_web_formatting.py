#!/usr/bin/env python3
"""
Test script for web application Indian formatting
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    # Test importing the web app
    import web.app
    print("✓ Successfully imported web application")
    
    # Test the formatting functions used in the web app
    from utils.formatting import (
        format_indian_currency, 
        format_indian_number_words,
        currency_filter,
        currency_short_filter,
        number_format_filter
    )
    
    print("✓ Successfully imported web formatting functions")
    
    # Test cases
    test_cases = [
        0,
        1000,
        100000,  # 1 lakh
        10000000,  # 1 crore
        123456789.50,
        9999999999.99
    ]
    
    print("\nTesting web application formatting functions:")
    print("-" * 60)
    print(f"{'Amount':>15} | {'Currency':>15} | {'Short':>10} | {'Number':>15}")
    print("-" * 60)
    
    for amount in test_cases:
        currency_fmt = currency_filter(amount)
        short_fmt = currency_short_filter(amount)
        number_fmt = number_format_filter(amount)
        print(f"{amount:>15,.2f} | {currency_fmt:>15} | {short_fmt:>10} | {number_fmt:>15}")
    
    print("\n✓ All web formatting tests passed!")
    
except ImportError as e:
    print(f"✗ Failed to import web application components: {e}")
    
except Exception as e:
    print(f"✗ Error during testing: {e}")