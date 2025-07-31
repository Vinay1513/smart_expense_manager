#!/usr/bin/env python3
"""
Test script for real PDF parsing
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expense_manager.settings')
django.setup()

from api.pdf_table_parser import PDFTableParser
from api.pdf_processor import PhonePePDFProcessor

def test_real_pdf():
    """Test PDF parsing with the actual uploaded PDF"""
    
    # Look for PDF files in the current directory
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found in current directory")
        print("Please place your PDF file in the backend directory and run this script")
        return
    
    print(f"Found PDF files: {pdf_files}")
    
    for pdf_file in pdf_files:
        print(f"\n{'='*50}")
        print(f"Testing PDF: {pdf_file}")
        print(f"{'='*50}")
        
        # Test with table parser
        print("\n1. Testing with PDF Table Parser:")
        try:
            parser = PDFTableParser()
            with open(pdf_file, 'rb') as f:
                transactions = parser.extract_transactions(f)
            
            print(f"Table parser found {len(transactions)} transactions")
            for i, t in enumerate(transactions[:5]):  # Show first 5
                print(f"  {i+1}. {t}")
                
        except Exception as e:
            print(f"Table parser error: {str(e)}")
        
        # Test with PhonePe processor
        print("\n2. Testing with PhonePe PDF Processor:")
        try:
            processor = PhonePePDFProcessor()
            with open(pdf_file, 'rb') as f:
                transactions = processor.extract_transactions(f)
            
            print(f"PhonePe processor found {len(transactions)} transactions")
            for i, t in enumerate(transactions[:5]):  # Show first 5
                print(f"  {i+1}. {t}")
                
        except Exception as e:
            print(f"PhonePe processor error: {str(e)}")

if __name__ == "__main__":
    test_real_pdf() 