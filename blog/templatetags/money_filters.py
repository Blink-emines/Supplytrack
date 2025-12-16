"""
Custom template filters for money formatting
Place this file in: blog/templatetags/money_filters.py
"""
from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='format_money')
def format_money(value):
    """
    Formats a number with space as thousand separator and comma for decimals.
    Example: 200100.33 -> "200 100,33"
    
    Usage in templates: {{ amount|format_money }}
    """
    if value is None or value == '':
        return '0,00'
    
    try:
        # Convert to Decimal for precision
        if isinstance(value, str):
            value = value.replace(',', '.').replace(' ', '')
        
        num = Decimal(str(value))
        
        # Split into integer and decimal parts
        int_part = int(abs(num))
        decimal_part = abs(num) - int_part
        
        # Format integer part with spaces
        int_str = f"{int_part:,}".replace(',', ' ')
        
        # Format decimal part
        decimal_str = f"{decimal_part:.2f}"[2:]  # Get ".xx" part and remove the dot
        
        # Add negative sign if needed
        sign = '-' if num < 0 else ''
        
        return f"{sign}{int_str},{decimal_str}"
    
    except (ValueError, TypeError, ArithmeticError):
        return '0,00'


@register.filter(name='format_money_short')
def format_money_short(value):
    """
    Formats large numbers in compact form with K/M suffixes.
    Example: 1500000 -> "1,5 M"
    
    Usage in templates: {{ amount|format_money_short }}
    """
    if value is None or value == '':
        return '0'
    
    try:
        num = float(value)
        
        if abs(num) >= 1_000_000:
            return f"{num/1_000_000:.1f}M".replace('.', ',')
        elif abs(num) >= 1_000:
            return f"{num/1_000:.1f}K".replace('.', ',')
        else:
            return format_money(value)
    
    except (ValueError, TypeError):
        return '0'