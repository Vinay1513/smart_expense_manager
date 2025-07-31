#!/usr/bin/env python3
"""
Test script for PDF processing
"""
import os
import sys
from io import BytesIO
from pdf_processor import PhonePePDFProcessor

def test_pdf_processing():
    """Test PDF processing with sample content"""
    
    # Sample PhonePe PDF content (you can replace this with actual content)
    sample_content = """
    PhonePe Transaction Statement
    
    Date: 15/01/2024
    Merchant: Amazon.in
    Amount: ₹1,299.00
    Status: Paid
    
    Date: 20/01/2024
    Merchant: Swiggy
    Amount: ₹450.50
    Status: Paid
    
    Date: 25/01/2024
    Merchant: Uber
    Amount: ₹120.00
    Status: Paid
    """
    
    print("Testing PDF processing with sample content...")
    print("Sample content:")
    print(sample_content)
    print("-" * 50)
    
    # Create a mock PDF file object
    class MockPDFFile:
        def __init__(self, content):
            self.content = content
            self.name = "test.pdf"
            self.size = len(content)
            self.content_type = "application/pdf"
        
        def read(self):
            return self.content.encode('utf-8')
    
    # Test the processor
    processor = PhonePePDFProcessor()
    
    # Test with sample lines
    lines = sample_content.split('\n')
    print("Testing line parsing:")
    for i, line in enumerate(lines):
        if line.strip():
            print(f"Line {i+1}: {line}")
            transaction = processor._parse_transaction_line(line)
            if transaction:
                print(f"  -> Parsed: {transaction}")
            else:
                print(f"  -> No transaction found")
    
    print("\n" + "=" * 50)
    print("Testing with different line formats:")
    
    # Test different line formats
    test_lines = [
        "15/01/2024  Amazon.in  ₹1,299.00  Paid",
        "20/01/2024  Swiggy  ₹450.50  Paid",
        "25/01/2024  Uber  ₹120.00  Paid",
        "Amazon.in  15/01/2024  ₹1,299.00",
        "₹1,299.00  15/01/2024  Amazon.in",
        "15-01-2024  Amazon.in  ₹1,299.00",
        "15/01/24  Amazon.in  ₹1,299.00",
        "Amazon.in  15/01/2024  ₹1,299.00  Success",
    ]
    
    for line in test_lines:
        print(f"Testing: {line}")
        transaction = processor._parse_transaction_line(line)
        if transaction:
            print(f"  -> Success: {transaction}")
        else:
            print(f"  -> Failed to parse")

if __name__ == "__main__":
    test_pdf_processing() 