#!/usr/bin/env python3
"""
Script to create a sample PhonePe PDF for testing
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import os

def create_sample_phonepe_pdf():
    """Create a sample PhonePe PDF with transaction data"""
    
    filename = "sample_phonepe_transactions.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1*inch, 10*inch, "PhonePe Transaction Statement")
    
    # Header
    c.setFont("Helvetica", 12)
    c.drawString(1*inch, 9.5*inch, "Date: 15 January 2024")
    c.drawString(1*inch, 9.2*inch, "Account: +91 98765 43210")
    
    # Table headers
    c.setFont("Helvetica-Bold", 10)
    c.drawString(1*inch, 8.5*inch, "Date")
    c.drawString(2.5*inch, 8.5*inch, "Merchant")
    c.drawString(5*inch, 8.5*inch, "Amount")
    c.drawString(7*inch, 8.5*inch, "Status")
    
    # Sample transactions
    transactions = [
        ("15/01/2024", "Amazon.in", "₹1,299.00", "Paid"),
        ("20/01/2024", "Swiggy", "₹450.50", "Paid"),
        ("25/01/2024", "Uber", "₹120.00", "Paid"),
        ("30/01/2024", "Netflix", "₹499.00", "Paid"),
        ("05/02/2024", "Flipkart", "₹2,500.00", "Paid"),
    ]
    
    y_position = 8.0
    c.setFont("Helvetica", 10)
    
    for date, merchant, amount, status in transactions:
        c.drawString(1*inch, y_position*inch, date)
        c.drawString(2.5*inch, y_position*inch, merchant)
        c.drawString(5*inch, y_position*inch, amount)
        c.drawString(7*inch, y_position*inch, status)
        y_position -= 0.3
    
    # Footer
    c.setFont("Helvetica", 8)
    c.drawString(1*inch, 1*inch, "This is a sample PhonePe transaction statement for testing purposes.")
    
    c.save()
    print(f"Sample PDF created: {filename}")
    return filename

if __name__ == "__main__":
    create_sample_phonepe_pdf() 