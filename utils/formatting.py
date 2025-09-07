#!/usr/bin/env python3
"""
Utility functions for Indian number formatting and file processing
"""

import re
import math
from typing import Union


def format_indian_currency(amount: Union[int, float], include_symbol: bool = True) -> str:
    """
    Format number in Indian currency format with proper comma placement
    
    Args:
        amount: The amount to format
        include_symbol: Whether to include ₹ symbol
    
    Returns:
        Formatted string like ₹1,23,45,678 or 1,23,45,678
    """
    if amount is None or amount == 0:
        return "₹0" if include_symbol else "0"
    
    # Handle negative numbers
    is_negative = amount < 0
    amount = abs(amount)
    
    # Convert to string and handle decimals
    if isinstance(amount, float) and amount != int(amount):
        amount_str = f"{amount:.2f}"
        integer_part, decimal_part = amount_str.split('.')
    else:
        integer_part = str(int(amount))
        decimal_part = None
    
    # Apply Indian comma system
    if len(integer_part) <= 3:
        formatted = integer_part
    else:
        # Last 3 digits
        last_three = integer_part[-3:]
        # Remaining digits
        remaining = integer_part[:-3]
        
        # Add commas every 2 digits for remaining part
        formatted_remaining = ""
        while len(remaining) > 2:
            formatted_remaining = "," + remaining[-2:] + formatted_remaining
            remaining = remaining[:-2]
        
        if remaining:
            formatted_remaining = remaining + formatted_remaining
        
        formatted = formatted_remaining + "," + last_three
    
    # Add decimal part if exists
    if decimal_part and decimal_part != "00":
        formatted += "." + decimal_part
    
    # Add negative sign
    if is_negative:
        formatted = "-" + formatted
    
    # Add rupee symbol
    if include_symbol:
        formatted = "₹" + formatted
    
    return formatted


def format_indian_number_words(amount: Union[int, float]) -> str:
    """
    Convert number to Indian words format (lakhs, crores)
    
    Args:
        amount: The amount to convert
    
    Returns:
        String like "12.5 Lakhs", "1.2 Crores"
    """
    if amount is None or amount == 0:
        return "₹0"
    
    is_negative = amount < 0
    amount = abs(amount)
    
    prefix = "₹"
    if is_negative:
        prefix += "-"
    
    if amount >= 10000000:  # 1 crore
        crores = amount / 10000000
        if crores >= 100:
            return f"{prefix}{crores:.0f} Cr"
        else:
            return f"{prefix}{crores:.1f} Cr"
    elif amount >= 100000:  # 1 lakh
        lakhs = amount / 100000
        if lakhs >= 100:
            return f"{prefix}{lakhs:.0f} L"
        else:
            return f"{prefix}{lakhs:.1f} L"
    elif amount >= 1000:  # 1 thousand
        thousands = amount / 1000
        return f"{prefix}{thousands:.1f} K"
    else:
        return f"{prefix}{amount:.0f}"


def get_smart_format(amount: Union[int, float]) -> dict:
    """
    Get both full and abbreviated formats
    
    Returns:
        Dict with 'full' and 'short' formats
    """
    return {
        'full': format_indian_currency(amount),
        'short': format_indian_number_words(amount)
    }


def extract_amount_from_text(text: str) -> list:
    """
    Extract monetary amounts from text using regex patterns
    
    Args:
        text: Input text to search
    
    Returns:
        List of found amounts as floats
    """
    # Patterns for Indian currency
    patterns = [
        r'₹\s*[\d,]+\.?\d*',  # ₹1,23,456.78
        r'Rs\.?\s*[\d,]+\.?\d*',  # Rs. 123456.78 or Rs 123456
        r'INR\s*[\d,]+\.?\d*',  # INR 123456.78
        r'rupees?\s*[\d,]+\.?\d*',  # rupees 123456
        r'[\d,]+\.?\d*\s*(?:crores?|lakhs?|thousands?)',  # 12.5 crores
    ]
    
    amounts = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Extract numeric value
            numeric_str = re.sub(r'[^\d.,]', '', match)
            numeric_str = numeric_str.replace(',', '')
            try:
                amount = float(numeric_str)
                amounts.append(amount)
            except ValueError:
                continue
    
    return amounts


def parse_indian_amount(amount_str: str) -> float:
    """
    Parse Indian formatted amount string to float
    
    Args:
        amount_str: String like "₹1,23,456.78" or "12.5 Lakhs"
    
    Returns:
        Float value
    """
    if not amount_str:
        return 0.0
    
    # Clean the string
    clean_str = amount_str.strip().lower()
    
    # Handle word formats
    if 'crore' in clean_str or 'cr' in clean_str:
        numeric_part = re.search(r'[\d.]+', clean_str)
        if numeric_part:
            return float(numeric_part.group()) * 10000000
    
    if 'lakh' in clean_str or ' l' in clean_str:
        numeric_part = re.search(r'[\d.]+', clean_str)
        if numeric_part:
            return float(numeric_part.group()) * 100000
    
    if 'thousand' in clean_str or ' k' in clean_str:
        numeric_part = re.search(r'[\d.]+', clean_str)
        if numeric_part:
            return float(numeric_part.group()) * 1000
    
    # Handle regular numeric format
    numeric_str = re.sub(r'[^\d.]', '', amount_str)
    try:
        return float(numeric_str)
    except ValueError:
        return 0.0


def calculate_percentage_change(old_value: float, new_value: float) -> tuple:
    """
    Calculate percentage change between two values
    
    Returns:
        Tuple of (percentage_change, direction, color_class)
    """
    if old_value == 0:
        if new_value > 0:
            return (100.0, "up", "success")
        else:
            return (0.0, "same", "secondary")
    
    percentage = ((new_value - old_value) / abs(old_value)) * 100
    
    if percentage > 0:
        return (percentage, "up", "success")
    elif percentage < 0:
        return (abs(percentage), "down", "danger")
    else:
        return (0.0, "same", "secondary")


# Template filter functions for Jinja2
def currency_filter(value):
    """Jinja2 filter for currency formatting"""
    return format_indian_currency(value)


def currency_short_filter(value):
    """Jinja2 filter for short currency formatting"""
    return format_indian_number_words(value)


def number_format_filter(value):
    """Jinja2 filter for number formatting without currency"""
    return format_indian_currency(value, include_symbol=False)
