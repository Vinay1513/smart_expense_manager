import pdfplumber
import re
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class PhonePePDFProcessor:
    """Processor for extracting transaction data from PhonePe PDF statements"""
    
    def __init__(self):
        self.transactions = []
    
    def extract_transactions(self, pdf_file) -> List[Dict[str, Any]]:
        """
        Extract transaction data from PhonePe PDF file
        
        Args:
            pdf_file: Uploaded PDF file object
            
        Returns:
            List of transaction dictionaries
        """
        try:
            print(f"Starting PDF processing for file: {pdf_file.name}")
            
            with pdfplumber.open(pdf_file) as pdf:
                print(f"PDF opened successfully, pages: {len(pdf.pages)}")
                transactions = []
                
                for i, page in enumerate(pdf.pages):
                    print(f"Processing page {i+1}")
                    text = page.extract_text()
                    if text:
                        print(f"Page {i+1} text length: {len(text)}")
                        print(f"Page {i+1} text content (first 500 chars): {text[:500]}")
                        page_transactions = self._parse_page_text(text)
                        print(f"Page {i+1} transactions found: {len(page_transactions)}")
                        transactions.extend(page_transactions)
                    else:
                        print(f"Page {i+1} has no extractable text")
                
                print(f"Total transactions before deduplication: {len(transactions)}")
                
                # Remove duplicates and sort by date
                unique_transactions = self._deduplicate_transactions(transactions)
                unique_transactions.sort(key=lambda x: x['transaction_date'])
                
                print(f"Final unique transactions: {len(unique_transactions)}")
                return unique_transactions
                
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            print(f"PDF processing error: {str(e)}")
            raise ValueError(f"Failed to process PDF file: {str(e)}")
    
    def _parse_page_text(self, text: str) -> List[Dict[str, Any]]:
        """Parse text from a PDF page to extract transactions"""
        transactions = []
        lines = text.split('\n')
        
        print(f"Total lines in page: {len(lines)}")
        for i, line in enumerate(lines):
            if i < 10:  # Print first 10 lines for debugging
                print(f"Line {i+1}: {line}")
            transaction = self._parse_transaction_line(line)
            if transaction:
                transactions.append(transaction)
        
        # If no transactions found with standard parsing, try alternative methods
        if not transactions:
            print("No transactions found with standard parsing, trying alternative methods...")
            transactions = self._parse_alternative_formats(text)
        
        return transactions
    
    def _parse_transaction_line(self, line: str) -> Dict[str, Any] | None:
        """
        Parse a single line to extract transaction information
        
        PhonePe PDF typically has lines like:
        "12/01/2024  Amazon.in  ₹1,299.00  Paid"
        "15/01/2024  Swiggy  ₹450.50  Paid"
        """
        # Remove extra whitespace
        line = line.strip()
        if not line:
            return None
        
        # Common patterns for PhonePe transaction lines
        patterns = [
            # Pattern 1: Date Merchant Amount Status
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})\s+(.+?)\s+(₹[\d,]+\.?\d*)\s+(Paid|Failed|Pending|Success)',
            # Pattern 2: Date Merchant Amount (without status)
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})\s+(.+?)\s+(₹[\d,]+\.?\d*)',
            # Pattern 3: Merchant Date Amount
            r'(.+?)\s+(\d{1,2}[/-]\d{1,2}[/-]\d{4})\s+(₹[\d,]+\.?\d*)',
            # Pattern 4: Date Amount Merchant
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})\s+(₹[\d,]+\.?\d*)\s+(.+?)',
            # Pattern 5: Amount Date Merchant
            r'(₹[\d,]+\.?\d*)\s+(\d{1,2}[/-]\d{1,2}[/-]\d{4})\s+(.+?)',
            # Pattern 6: More flexible date format
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+(.+?)\s+(₹[\d,]+\.?\d*)',
            # Pattern 7: Amount with decimal and merchant
            r'(\d+\.\d{2})\s+(.+?)\s+(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
            # Pattern 8: Merchant with amount and date
            r'(.+?)\s+(\d+\.\d{2})\s+(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
            # Pattern 9: YYYY-MM-DD format with Rs. amount
            r'(\d{4}-\d{2}-\d{2})\s+[A-Z0-9]+\s+(.+?)\s+Rs\.\s*([\d,]+\.?\d*)\s+(Debit|Credit)',
            # Pattern 10: YYYY-MM-DD format with Rs. amount (simplified)
            r'(\d{4}-\d{2}-\d{2})\s+(.+?)\s+Rs\.\s*([\d,]+\.?\d*)',
            # Pattern 11: Month name format (Jul 16, 2025) with DEBIT and ₹
            r'(\w{3}\s+\d{1,2},\s+\d{4})\s+(.+?)\s+DEBIT\s+₹([\d,]+\.?\d*)',
            # Pattern 12: Month name format with CREDIT and ₹
            r'(\w{3}\s+\d{1,2},\s+\d{4})\s+(.+?)\s+CREDIT\s+₹([\d,]+\.?\d*)',
            # Pattern 13: Month name format with any transaction type
            r'(\w{3}\s+\d{1,2},\s+\d{4})\s+(.+?)\s+(DEBIT|CREDIT)\s+₹([\d,]+\.?\d*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    if pattern == patterns[0]:  # Pattern 1
                        date_str, merchant, amount_str, status = match.groups()
                        transaction_date = self._parse_date(date_str)
                        amount = self._parse_amount(amount_str)
                        
                        return {
                            'transaction_date': transaction_date,
                            'merchant_name': merchant.strip(),
                            'amount': amount,
                            'payment_method': 'PhonePe',
                            'status': status
                        }
                    
                    elif pattern == patterns[1]:  # Pattern 2
                        date_str, merchant, amount_str = match.groups()
                        transaction_date = self._parse_date(date_str)
                        amount = self._parse_amount(amount_str)
                        
                        return {
                            'transaction_date': transaction_date,
                            'merchant_name': merchant.strip(),
                            'amount': amount,
                            'payment_method': 'PhonePe',
                            'status': 'Paid'
                        }
                    
                    elif pattern == patterns[2]:  # Pattern 3
                        merchant, date_str, amount_str = match.groups()
                        transaction_date = self._parse_date(date_str)
                        amount = self._parse_amount(amount_str)
                        
                        return {
                            'transaction_date': transaction_date,
                            'merchant_name': merchant.strip(),
                            'amount': amount,
                            'payment_method': 'PhonePe',
                            'status': 'Paid'
                        }
                    
                    elif pattern == patterns[3]:  # Pattern 4
                        date_str, amount_str, merchant = match.groups()
                        transaction_date = self._parse_date(date_str)
                        amount = self._parse_amount(amount_str)
                        
                        return {
                            'transaction_date': transaction_date,
                            'merchant_name': merchant.strip(),
                            'amount': amount,
                            'payment_method': 'PhonePe',
                            'status': 'Paid'
                        }
                    
                    elif pattern == patterns[4]:  # Pattern 5
                        amount_str, date_str, merchant = match.groups()
                        transaction_date = self._parse_date(date_str)
                        amount = self._parse_amount(amount_str)
                        
                        return {
                            'transaction_date': transaction_date,
                            'merchant_name': merchant.strip(),
                            'amount': amount,
                            'payment_method': 'PhonePe',
                            'status': 'Paid'
                        }
                    
                    elif pattern == patterns[5]:  # Pattern 6
                        date_str, merchant, amount_str = match.groups()
                        transaction_date = self._parse_date(date_str)
                        amount = self._parse_amount(amount_str)
                        
                        return {
                            'transaction_date': transaction_date,
                            'merchant_name': merchant.strip(),
                            'amount': amount,
                            'payment_method': 'PhonePe',
                            'status': 'Paid'
                        }
                    
                    elif pattern == patterns[6]:  # Pattern 7
                        amount_str, merchant, date_str = match.groups()
                        transaction_date = self._parse_date(date_str)
                        amount = self._parse_amount(f"₹{amount_str}")
                        
                        return {
                            'transaction_date': transaction_date,
                            'merchant_name': merchant.strip(),
                            'amount': amount,
                            'payment_method': 'PhonePe',
                            'status': 'Paid'
                        }
                    
                    elif pattern == patterns[7]:  # Pattern 8
                        merchant, amount_str, date_str = match.groups()
                        transaction_date = self._parse_date(date_str)
                        amount = self._parse_amount(f"₹{amount_str}")
                        
                        return {
                            'transaction_date': transaction_date,
                            'merchant_name': merchant.strip(),
                            'amount': amount,
                            'payment_method': 'PhonePe',
                            'status': 'Paid'
                        }
                    
                    elif pattern == patterns[8]:  # Pattern 9
                        date_str, merchant, amount_str, transaction_type = match.groups()
                        transaction_date = self._parse_date(date_str)
                        amount = self._parse_amount(f"₹{amount_str}")
                        
                        return {
                            'transaction_date': transaction_date,
                            'merchant_name': merchant.strip(),
                            'amount': amount,
                            'payment_method': 'PhonePe',
                            'status': 'Paid' if transaction_type == 'Debit' else 'Received'
                        }
                    
                    elif pattern == patterns[9]:  # Pattern 10
                        date_str, merchant, amount_str = match.groups()
                        transaction_date = self._parse_date(date_str)
                        amount = self._parse_amount(f"₹{amount_str}")
                        
                        return {
                            'transaction_date': transaction_date,
                            'merchant_name': merchant.strip(),
                            'amount': amount,
                            'payment_method': 'PhonePe',
                            'status': 'Paid'
                        }
                    
                    elif pattern == patterns[10]:  # Pattern 11
                        date_str, merchant, amount_str = match.groups()
                        transaction_date = self._parse_date(date_str)
                        amount = self._parse_amount(f"₹{amount_str}")
                        
                        return {
                            'transaction_date': transaction_date,
                            'merchant_name': merchant.strip(),
                            'amount': amount,
                            'payment_method': 'PhonePe',
                            'status': 'Paid'
                        }
                    
                    elif pattern == patterns[11]:  # Pattern 12
                        date_str, merchant, amount_str = match.groups()
                        transaction_date = self._parse_date(date_str)
                        amount = self._parse_amount(f"₹{amount_str}")
                        
                        return {
                            'transaction_date': transaction_date,
                            'merchant_name': merchant.strip(),
                            'amount': amount,
                            'payment_method': 'PhonePe',
                            'status': 'Received'
                        }
                    
                    elif pattern == patterns[12]:  # Pattern 13
                        date_str, merchant, transaction_type, amount_str = match.groups()
                        transaction_date = self._parse_date(date_str)
                        amount = self._parse_amount(f"₹{amount_str}")
                        
                        return {
                            'transaction_date': transaction_date,
                            'merchant_name': merchant.strip(),
                            'amount': amount,
                            'payment_method': 'PhonePe',
                            'status': 'Paid' if transaction_type == 'DEBIT' else 'Received'
                        }
                        
                except (ValueError, AttributeError) as e:
                    logger.warning(f"Failed to parse line: {line}, error: {str(e)}")
                    continue
        
        return None
    
    def _parse_alternative_formats(self, text: str) -> List[Dict[str, Any]]:
        """Parse text using alternative methods when standard parsing fails"""
        transactions = []
        
        # Method 1: Look for date patterns and extract surrounding text
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{4}-\d{2}-\d{2})',  # 2025-07-30
            r'(\w{3}\s+\d{1,2},\s+\d{4})',  # Jul 16, 2025
            r'(\d{1,2}\s+\w{3}\s+\d{4})',  # 15 Jan 2024
            r'(\d{1,2}\s+\w+\s+\d{4})',  # 15 January 2024
        ]
        
        for date_pattern in date_patterns:
            matches = re.finditer(date_pattern, text)
            for match in matches:
                try:
                    date_str = match.group(1)
                    # Get surrounding text (up to 100 characters before and after)
                    start = max(0, match.start() - 100)
                    end = min(len(text), match.end() + 100)
                    context = text[start:end]
                    
                    # Try to extract amount and merchant from context
                    amount_match = re.search(r'(?:₹|Rs\.)\s*[\d,]+\.?\d*', context)
                    if amount_match:
                        amount_str = amount_match.group(0)
                        amount = self._parse_amount(amount_str)
                        
                        # Extract merchant name (text between date and amount, or before date)
                        merchant = self._extract_merchant_from_context(context, date_str, amount_str)
                        
                        if merchant:
                            transaction_date = self._parse_date(date_str)
                            transactions.append({
                                'transaction_date': transaction_date,
                                'merchant_name': merchant.strip(),
                                'amount': amount,
                                'payment_method': 'PhonePe',
                                'status': 'Paid'
                            })
                            
                except Exception as e:
                    print(f"Error in alternative parsing: {str(e)}")
                    continue
        
        return transactions
    
    def _extract_merchant_from_context(self, context: str, date_str: str, amount_str: str) -> str:
        """Extract merchant name from context text"""
        try:
            # Remove date and amount from context
            clean_context = context.replace(date_str, '').replace(amount_str, '')
            
            # Look for common merchant patterns
            merchant_patterns = [
                r'([A-Za-z0-9\s\.]+(?:\.in|\.com|\.co\.in))',  # Amazon.in, Flipkart.com
                r'([A-Za-z]+(?:\s+[A-Za-z]+)*)',  # General text
            ]
            
            for pattern in merchant_patterns:
                matches = re.findall(pattern, clean_context)
                for match in matches:
                    merchant = match.strip()
                    if len(merchant) > 2 and not merchant.isdigit():
                        return merchant
            
            return "Unknown Merchant"
            
        except Exception as e:
            print(f"Error extracting merchant: {str(e)}")
            return "Unknown Merchant"
    
    def _parse_date(self, date_str: str) -> datetime.date:
        """Parse date string to datetime.date object"""
        try:
            # Handle different date formats
            formats = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d/%m/%y', '%d-%m-%y', '%Y-%m-%d']
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
            
            # Handle month names (e.g., "15 Jan 2024" or "Jul 16, 2025")
            month_names = {
                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
            }
            
            # Pattern for "Jul 16, 2025" format
            month_pattern1 = r'(\w{3})\s+(\d{1,2}),\s+(\d{4})'
            month_match1 = re.search(month_pattern1, date_str, re.IGNORECASE)
            if month_match1:
                month_name, day, year = month_match1.groups()
                month = month_names.get(month_name.lower()[:3])
                if month:
                    return datetime(int(year), month, int(day)).date()
            
            # Pattern for "15 Jan 2024" format
            month_pattern2 = r'(\d{1,2})\s+(\w{3})\s+(\d{4})'
            month_match2 = re.search(month_pattern2, date_str, re.IGNORECASE)
            if month_match2:
                day, month_name, year = month_match2.groups()
                month = month_names.get(month_name.lower()[:3])
                if month:
                    return datetime(int(year), month, int(day)).date()
            
            # If no format matches, try to extract date using regex
            date_match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', date_str)
            if date_match:
                day, month, year = date_match.groups()
                # Handle 2-digit years
                if len(year) == 2:
                    year = '20' + year
                return datetime(int(year), int(month), int(day)).date()
            
            raise ValueError(f"Unable to parse date: {date_str}")
            
        except Exception as e:
            logger.error(f"Date parsing error: {str(e)}")
            raise ValueError(f"Invalid date format: {date_str}")
    
    def _parse_amount(self, amount_str: str) -> Decimal:
        """Parse amount string to Decimal"""
        try:
            # Remove currency symbol and commas
            clean_amount = re.sub(r'[₹$Rs\.\s,]', '', amount_str)
            
            # Handle different decimal separators
            if '.' in clean_amount:
                amount = Decimal(clean_amount)
            else:
                # Assume it's in paise if no decimal point
                amount = Decimal(clean_amount) / 100
            
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            return amount
            
        except Exception as e:
            logger.error(f"Amount parsing error: {str(e)}")
            raise ValueError(f"Invalid amount format: {amount_str}")
    
    def _deduplicate_transactions(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate transactions based on date, merchant, and amount"""
        seen = set()
        unique_transactions = []
        
        for transaction in transactions:
            # Create a unique key for each transaction
            key = (
                transaction['transaction_date'],
                transaction['merchant_name'].lower().strip(),
                transaction['amount']
            )
            
            if key not in seen:
                seen.add(key)
                unique_transactions.append(transaction)
        
        return unique_transactions
    
    def categorize_merchant(self, merchant_name: str) -> str:
        """
        Categorize merchant based on name patterns
        
        Args:
            merchant_name: Name of the merchant
            
        Returns:
            Category name
        """
        merchant_lower = merchant_name.lower()
        
        # Food & Dining
        food_keywords = ['swiggy', 'zomato', 'dominos', 'pizza', 'restaurant', 'cafe', 'food', 'dining']
        if any(keyword in merchant_lower for keyword in food_keywords):
            return 'Food & Dining'
        
        # Shopping
        shopping_keywords = ['amazon', 'flipkart', 'myntra', 'shop', 'store', 'mall', 'retail']
        if any(keyword in merchant_lower for keyword in shopping_keywords):
            return 'Shopping'
        
        # Transportation
        transport_keywords = ['uber', 'ola', 'metro', 'bus', 'train', 'fuel', 'petrol', 'diesel']
        if any(keyword in merchant_lower for keyword in transport_keywords):
            return 'Transportation'
        
        # Entertainment
        entertainment_keywords = ['netflix', 'prime', 'hotstar', 'movie', 'cinema', 'theatre', 'game']
        if any(keyword in merchant_lower for keyword in entertainment_keywords):
            return 'Entertainment'
        
        # Utilities
        utility_keywords = ['electricity', 'water', 'gas', 'internet', 'mobile', 'phone', 'bill']
        if any(keyword in merchant_lower for keyword in utility_keywords):
            return 'Utilities'
        
        # Healthcare
        health_keywords = ['pharmacy', 'medical', 'hospital', 'doctor', 'clinic', 'health']
        if any(keyword in merchant_lower for keyword in health_keywords):
            return 'Healthcare'
        
        # Education
        education_keywords = ['school', 'college', 'university', 'course', 'training', 'education']
        if any(keyword in merchant_lower for keyword in education_keywords):
            return 'Education'
        
        # Default category
        return 'Other' 