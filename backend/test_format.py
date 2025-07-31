#!/usr/bin/env python3
"""
Test script for the new PhonePe format parsing
"""
import re
from datetime import datetime
from decimal import Decimal

def test_phonepe_format():
    """Test the new PhonePe format parsing"""
    
    # Test lines from your actual PDF
    test_lines = [
        "Jul 16, 2025 Mobile recharged 9689718455 DEBIT ₹302",
        "Jul 13, 2025 Paid to Todakar Chiken Centre DEBIT ₹210",
        "Jul 13, 2025 Paid to Laxmi Sweet Home DEBIT ₹20",
        "Jul 07, 2025 Paid to Mama 2 DEBIT ₹150",
        "Jul 05, 2025 Paid to SBIMOPS DEBIT ₹100",
    ]
    
    # Test the new regex patterns
    patterns = [
        # Pattern 11: Month name format (Jul 16, 2025) with DEBIT and ₹
        r'(\w{3}\s+\d{1,2},\s+\d{4})\s+(.+?)\s+DEBIT\s+₹([\d,]+\.?\d*)',
        # Pattern 12: Month name format with CREDIT and ₹
        r'(\w{3}\s+\d{1,2},\s+\d{4})\s+(.+?)\s+CREDIT\s+₹([\d,]+\.?\d*)',
        # Pattern 13: Month name format with any transaction type
        r'(\w{3}\s+\d{1,2},\s+\d{4})\s+(.+?)\s+(DEBIT|CREDIT)\s+₹([\d,]+\.?\d*)',
    ]
    
    print("Testing PhonePe format parsing...")
    print("=" * 50)
    
    for i, line in enumerate(test_lines):
        print(f"\nTest line {i+1}: {line}")
        
        for j, pattern in enumerate(patterns):
            match = re.search(pattern, line)
            if match:
                print(f"  Pattern {j+1} matched!")
                groups = match.groups()
                print(f"  Groups: {groups}")
                
                # Parse date
                date_str = groups[0]
                month_names = {
                    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
                }
                
                month_pattern = r'(\w{3})\s+(\d{1,2}),\s+(\d{4})'
                month_match = re.search(month_pattern, date_str, re.IGNORECASE)
                if month_match:
                    month_name, day, year = month_match.groups()
                    month = month_names.get(month_name.lower()[:3])
                    if month:
                        parsed_date = datetime(int(year), month, int(day)).date()
                        print(f"  Parsed date: {parsed_date}")
                
                # Parse amount
                amount_str = groups[-1]  # Last group is always amount
                clean_amount = re.sub(r'[₹$Rs\.\s,]', '', amount_str)
                parsed_amount = Decimal(clean_amount)
                print(f"  Parsed amount: {parsed_amount}")
                
                # Parse description
                if len(groups) == 3:
                    description = groups[1]
                elif len(groups) == 4:
                    description = groups[1]
                print(f"  Parsed description: {description}")
                
                break
        else:
            print("  No pattern matched!")

if __name__ == "__main__":
    test_phonepe_format() 