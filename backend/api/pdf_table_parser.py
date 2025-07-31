import pdfplumber
import re
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ParsedTransaction:
    """Data class for parsed transaction data"""
    transaction_id: Optional[str] = None
    date: Optional[datetime.date] = None
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    transaction_type: str = 'debit'
    status: str = 'success'
    raw_data: Dict[str, Any] = None


class PDFTableParser:
    """Advanced PDF table parser for transaction statements"""
    
    def __init__(self):
        self.date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
            r'(\d{2}-\d{2}-\d{4})',  # DD-MM-YYYY
            r'(\d{2}/\d{2}/\d{4})',  # DD/MM/YYYY
            r'(\d{4}/\d{2}/\d{2})',  # YYYY/MM/DD
            r'(\w{3}\s+\d{1,2},\s+\d{4})',  # Jul 16, 2025
        ]
        
        self.amount_patterns = [
            r'Rs\.\s*([\d,]+\.?\d*)',
            r'₹\s*([\d,]+\.?\d*)',
            r'([\d,]+\.?\d*)\s*Rs',
            r'([\d,]+\.?\d*)\s*₹',
            r'([\d,]+\.?\d*)',  # Just numbers
        ]
        
        self.transaction_id_patterns = [
            r'TXN\d+',
            r'[A-Z]{2,3}\d{6,}',
            r'\d{10,}',
        ]
        
        self.credit_keywords = [
            'credit', 'received', 'credited', 'incoming', 'deposit',
            'refund', 'cashback', 'reward', 'bonus', 'interest'
        ]
        
        self.debit_keywords = [
            'debit', 'paid', 'sent', 'outgoing', 'withdrawal',
            'purchase', 'payment', 'bill', 'recharge', 'transfer'
        ]
        
        self.status_keywords = {
            'success': ['success', 'completed', 'successful', 'done'],
            'failed': ['failed', 'declined', 'rejected', 'error'],
            'pending': ['pending', 'processing', 'in progress']
        }
    
    def extract_transactions(self, pdf_file) -> List[Dict[str, Any]]:
        """
        Extract transactions from PDF file using table detection
        
        Args:
            pdf_file: Uploaded PDF file object
            
        Returns:
            List of transaction dictionaries
        """
        try:
            print(f"Starting PDF table processing for file: {pdf_file.name}")
            
            with pdfplumber.open(pdf_file) as pdf:
                print(f"PDF opened successfully, pages: {len(pdf.pages)}")
                all_transactions = []
                
                for i, page in enumerate(pdf.pages):
                    print(f"Processing page {i+1}")
                    page_transactions = self._process_page(page, i+1)
                    all_transactions.extend(page_transactions)
                
                print(f"Total transactions found: {len(all_transactions)}")
                
                # Remove duplicates and sort by date
                unique_transactions = self._deduplicate_transactions(all_transactions)
                unique_transactions.sort(key=lambda x: x['date'])
                
                print(f"Final unique transactions: {len(unique_transactions)}")
                return unique_transactions
                
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            print(f"PDF processing error: {str(e)}")
            raise ValueError(f"Failed to process PDF file: {str(e)}")
    
    def _process_page(self, page, page_num: int) -> List[Dict[str, Any]]:
        """Process a single page to extract transactions"""
        transactions = []
        
        # Extract text for debugging
        text = page.extract_text()
        print(f"Page {page_num} text length: {len(text)}")
        print(f"Page {page_num} text preview: {text[:200]}...")
        
        # Try to find tables
        tables = page.find_tables()
        print(f"Page {page_num} tables found: {len(tables)}")
        
        if tables:
            # Process each table
            for table_idx, table in enumerate(tables):
                print(f"Processing table {table_idx + 1} on page {page_num}")
                table_transactions = self._process_table(table, page_num, table_idx)
                transactions.extend(table_transactions)
        else:
            # Fallback to text parsing if no tables found
            print(f"No tables found on page {page_num}, using text parsing")
            text_transactions = self._parse_text_for_transactions(text, page_num)
            transactions.extend(text_transactions)
        
        return transactions
    
    def _process_table(self, table, page_num: int, table_idx: int) -> List[Dict[str, Any]]:
        """Process a table to extract transactions"""
        transactions = []
        
        # Convert table to list of lists
        table_data = []
        for row in table:
            row_data = []
            for cell in row:
                if cell is not None:
                    row_data.append(cell.strip() if isinstance(cell, str) else str(cell))
                else:
                    row_data.append("")
            table_data.append(row_data)
        
        print(f"Table {table_idx + 1} has {len(table_data)} rows")
        
        # Detect header row and data rows
        header_row, data_rows = self._separate_header_and_data(table_data)
        
        if header_row:
            print(f"Header detected: {header_row}")
            # Map columns based on header
            column_mapping = self._map_columns_from_header(header_row)
        else:
            # Try to infer column mapping from first few rows
            column_mapping = self._infer_column_mapping(table_data[:5])
        
        print(f"Column mapping: {column_mapping}")
        
        # Process each data row
        for row_idx, row in enumerate(data_rows):
            if not any(cell.strip() for cell in row):
                continue  # Skip empty rows
                
            print(f"Processing row {row_idx + 1}: {row}")
            transaction = self._parse_table_row(row, column_mapping, page_num, table_idx, row_idx)
            if transaction:
                transactions.append(transaction)
        
        return transactions
    
    def _separate_header_and_data(self, table_data: List[List[str]]) -> Tuple[Optional[List[str]], List[List[str]]]:
        """Separate header row from data rows"""
        if not table_data:
            return None, []
        
        # Check if first row looks like a header
        first_row = table_data[0]
        header_keywords = ['date', 'description', 'amount', 'type', 'transaction', 'id', 'status']
        
        first_row_lower = ' '.join(first_row).lower()
        is_header = any(keyword in first_row_lower for keyword in header_keywords)
        
        if is_header:
            return first_row, table_data[1:]
        else:
            return None, table_data
    
    def _map_columns_from_header(self, header_row: List[str]) -> Dict[str, int]:
        """Map column names to indices based on header"""
        mapping = {}
        header_lower = [col.lower() for col in header_row]
        
        for idx, col in enumerate(header_lower):
            if any(keyword in col for keyword in ['date', 'time']):
                mapping['date'] = idx
            elif any(keyword in col for keyword in ['description', 'desc', 'merchant', 'payee', 'details']):
                mapping['description'] = idx
            elif any(keyword in col for keyword in ['amount', 'amt', 'value', 'sum']):
                mapping['amount'] = idx
            elif any(keyword in col for keyword in ['type', 'transaction_type', 'credit', 'debit']):
                mapping['type'] = idx
            elif any(keyword in col for keyword in ['id', 'transaction_id', 'ref', 'reference']):
                mapping['transaction_id'] = idx
            elif any(keyword in col for keyword in ['status', 'state']):
                mapping['status'] = idx
        
        return mapping
    
    def _infer_column_mapping(self, sample_rows: List[List[str]]) -> Dict[str, int]:
        """Infer column mapping from sample data"""
        if not sample_rows:
            return {}
        
        # Analyze each column
        num_cols = len(sample_rows[0])
        column_analysis = []
        
        for col_idx in range(num_cols):
            col_data = [row[col_idx] if col_idx < len(row) else "" for row in sample_rows]
            analysis = self._analyze_column(col_data)
            column_analysis.append(analysis)
        
        # Map based on analysis
        mapping = {}
        for col_idx, analysis in enumerate(column_analysis):
            if analysis['is_date']:
                mapping['date'] = col_idx
            elif analysis['is_amount']:
                mapping['amount'] = col_idx
            elif analysis['is_description']:
                mapping['description'] = col_idx
            elif analysis['is_type']:
                mapping['type'] = col_idx
            elif analysis['is_id']:
                mapping['transaction_id'] = col_idx
        
        return mapping
    
    def _analyze_column(self, column_data: List[str]) -> Dict[str, Any]:
        """Analyze a column to determine its type"""
        analysis = {
            'is_date': False,
            'is_amount': False,
            'is_description': False,
            'is_type': False,
            'is_id': False,
            'date_count': 0,
            'amount_count': 0,
            'type_count': 0,
            'id_count': 0,
        }
        
        for cell in column_data:
            cell = cell.strip()
            if not cell:
                continue
            
            # Check for date patterns
            for pattern in self.date_patterns:
                if re.search(pattern, cell):
                    analysis['date_count'] += 1
                    break
            
            # Check for amount patterns
            for pattern in self.amount_patterns:
                if re.search(pattern, cell):
                    analysis['amount_count'] += 1
                    break
            
            # Check for transaction type
            cell_lower = cell.lower()
            if any(keyword in cell_lower for keyword in self.credit_keywords + self.debit_keywords):
                analysis['type_count'] += 1
            
            # Check for transaction ID
            for pattern in self.transaction_id_patterns:
                if re.search(pattern, cell):
                    analysis['id_count'] += 1
                    break
        
        # Determine column type based on counts
        total_cells = len([c for c in column_data if c.strip()])
        if total_cells > 0:
            if analysis['date_count'] / total_cells > 0.5:
                analysis['is_date'] = True
            elif analysis['amount_count'] / total_cells > 0.5:
                analysis['is_amount'] = True
            elif analysis['type_count'] / total_cells > 0.3:
                analysis['is_type'] = True
            elif analysis['id_count'] / total_cells > 0.5:
                analysis['is_id'] = True
            else:
                analysis['is_description'] = True
        
        return analysis
    
    def _parse_table_row(self, row: List[str], column_mapping: Dict[str, int], 
                         page_num: int, table_idx: int, row_idx: int) -> Optional[Dict[str, Any]]:
        """Parse a single table row into a transaction"""
        try:
            parsed = ParsedTransaction()
            parsed.raw_data = {
                'page': page_num,
                'table': table_idx,
                'row': row_idx,
                'raw_row': row
            }
            
            # Extract fields based on mapping
            for field, col_idx in column_mapping.items():
                if col_idx < len(row):
                    value = row[col_idx].strip()
                    if value:
                        if field == 'date':
                            parsed.date = self._parse_date(value)
                        elif field == 'description':
                            parsed.description = value
                        elif field == 'amount':
                            parsed.amount = self._parse_amount(value)
                        elif field == 'type':
                            parsed.transaction_type = self._parse_transaction_type(value)
                        elif field == 'transaction_id':
                            parsed.transaction_id = value
                        elif field == 'status':
                            parsed.status = self._parse_status(value)
            
            # If no explicit mapping, try to infer fields
            if not parsed.date:
                parsed.date = self._find_date_in_row(row)
            
            if not parsed.description:
                parsed.description = self._find_description_in_row(row)
            
            if not parsed.amount:
                parsed.amount = self._find_amount_in_row(row)
            
            if not parsed.transaction_type:
                parsed.transaction_type = self._infer_transaction_type(row)
            
            if not parsed.transaction_id:
                parsed.transaction_id = self._find_transaction_id_in_row(row)
            
            # Validate required fields
            if not parsed.date or not parsed.description or not parsed.amount:
                print(f"Skipping row {row_idx + 1}: missing required fields")
                return None
            
            # Convert to dictionary
            transaction_dict = {
                'transaction_id': parsed.transaction_id,
                'date': parsed.date,
                'description': parsed.description,
                'amount': parsed.amount,
                'transaction_type': parsed.transaction_type,
                'status': parsed.status,
                'payment_method': 'UPI',
                'source_file': 'PDF Upload',
                'raw_data': parsed.raw_data
            }
            
            print(f"Parsed transaction: {transaction_dict}")
            return transaction_dict
            
        except Exception as e:
            print(f"Error parsing row {row_idx + 1}: {str(e)}")
            return None
    
    def _parse_text_for_transactions(self, text: str, page_num: int) -> List[Dict[str, Any]]:
        """Parse text for transactions when no tables are found"""
        transactions = []
        lines = text.split('\n')
        
        for line_idx, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Try to parse as a transaction line
            transaction = self._parse_transaction_line(line, page_num, line_idx)
            if transaction:
                transactions.append(transaction)
        
        return transactions
    
    def _parse_transaction_line(self, line: str, page_num: int, line_idx: int) -> Optional[Dict[str, Any]]:
        """Parse a single line for transaction data"""
        try:
            # Look for date patterns
            date_match = None
            for pattern in self.date_patterns:
                date_match = re.search(pattern, line)
                if date_match:
                    break
            
            if not date_match:
                return None
            
            date_str = date_match.group(1)
            parsed_date = self._parse_date(date_str)
            
            # Look for amount patterns
            amount_match = None
            for pattern in self.amount_patterns:
                amount_match = re.search(pattern, line)
                if amount_match:
                    break
            
            if not amount_match:
                return None
            
            amount_str = amount_match.group(1)
            parsed_amount = self._parse_amount(amount_str)
            
            # Extract description (text between date and amount)
            date_start = date_match.start()
            amount_start = amount_match.start()
            
            if date_start < amount_start:
                description = line[date_start + len(date_str):amount_start].strip()
            else:
                description = line[amount_start + len(amount_str):date_start].strip()
            
            # Clean up description
            description = re.sub(r'[^\w\s\-\.]', ' ', description).strip()
            
            if not description:
                return None
            
            # Determine transaction type
            transaction_type = self._infer_transaction_type([line])
            
            return {
                'transaction_id': self._find_transaction_id_in_line(line),
                'date': parsed_date,
                'description': description,
                'amount': parsed_amount,
                'transaction_type': transaction_type,
                'status': 'success',
                'payment_method': 'UPI',
                'source_file': 'PDF Upload',
                'raw_data': {
                    'page': page_num,
                    'line': line_idx,
                    'raw_line': line
                }
            }
            
        except Exception as e:
            print(f"Error parsing line {line_idx + 1}: {str(e)}")
            return None
    
    def _parse_date(self, date_str: str) -> datetime.date:
        """Parse date string to datetime.date object"""
        try:
            # Handle different date formats
            formats = [
                '%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d',
                '%d-%m-%y', '%d/%m/%y', '%y-%m-%d', '%y/%m/%d'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
            
            # Handle month names (e.g., "Jul 16, 2025")
            month_names = {
                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
            }
            
            # Pattern for "Jul 16, 2025" format
            month_pattern = r'(\w{3})\s+(\d{1,2}),\s+(\d{4})'
            month_match = re.search(month_pattern, date_str, re.IGNORECASE)
            if month_match:
                month_name, day, year = month_match.groups()
                month = month_names.get(month_name.lower()[:3])
                if month:
                    return datetime(int(year), month, int(day)).date()
            
            raise ValueError(f"Unable to parse date: {date_str}")
            
        except Exception as e:
            logger.error(f"Date parsing error: {str(e)}")
            raise ValueError(f"Invalid date format: {date_str}")
    
    def _parse_amount(self, amount_str: str) -> Decimal:
        """Parse amount string to Decimal"""
        try:
            # Remove currency symbols and commas
            clean_amount = re.sub(r'[₹$Rs\.\s,]', '', amount_str)
            
            # Handle different decimal separators
            if '.' in clean_amount:
                amount = Decimal(clean_amount)
            else:
                # For amounts without decimal point, check if it's likely paise or rupees
                # If the amount is less than 1000 and the original string has ₹ or Rs, 
                # it's likely rupees, not paise
                if len(clean_amount) <= 3 and ('₹' in amount_str or 'Rs' in amount_str):
                    # Small amount with currency symbol - likely rupees
                    amount = Decimal(clean_amount)
                elif len(clean_amount) <= 2:
                    # Very small amount (1-99) - likely rupees, not paise
                    amount = Decimal(clean_amount)
                else:
                    # Larger amount without decimal - could be paise, but more likely rupees
                    # Only assume paise if it's a very large number (>10000)
                    if int(clean_amount) > 10000:
                        amount = Decimal(clean_amount) / 100
                    else:
                        amount = Decimal(clean_amount)
            
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            return amount
            
        except Exception as e:
            logger.error(f"Amount parsing error: {str(e)}")
            raise ValueError(f"Invalid amount format: {amount_str}")
    
    def _parse_transaction_type(self, type_str: str) -> str:
        """Parse transaction type from string"""
        type_lower = type_str.lower()
        
        if any(keyword in type_lower for keyword in self.credit_keywords):
            return 'credit'
        elif any(keyword in type_lower for keyword in self.debit_keywords):
            return 'debit'
        else:
            return 'debit'  # Default to debit
    
    def _parse_status(self, status_str: str) -> str:
        """Parse status from string"""
        status_lower = status_str.lower()
        
        for status, keywords in self.status_keywords.items():
            if any(keyword in status_lower for keyword in keywords):
                return status
        
        return 'success'  # Default to success
    
    def _find_date_in_row(self, row: List[str]) -> Optional[datetime.date]:
        """Find date in a row"""
        for cell in row:
            if not cell.strip():
                continue
            for pattern in self.date_patterns:
                match = re.search(pattern, cell)
                if match:
                    try:
                        return self._parse_date(match.group(1))
                    except:
                        continue
        return None
    
    def _find_description_in_row(self, row: List[str]) -> Optional[str]:
        """Find description in a row"""
        for cell in row:
            cell = cell.strip()
            if not cell:
                continue
            
            # Skip if it looks like a date, amount, or ID
            if any(re.search(pattern, cell) for pattern in self.date_patterns):
                continue
            if any(re.search(pattern, cell) for pattern in self.amount_patterns):
                continue
            if any(re.search(pattern, cell) for pattern in self.transaction_id_patterns):
                continue
            
            # Clean up the description
            description = re.sub(r'[^\w\s\-\.]', ' ', cell).strip()
            if len(description) > 2:
                return description
        
        return None
    
    def _find_amount_in_row(self, row: List[str]) -> Optional[Decimal]:
        """Find amount in a row"""
        for cell in row:
            if not cell.strip():
                continue
            for pattern in self.amount_patterns:
                match = re.search(pattern, cell)
                if match:
                    try:
                        return self._parse_amount(match.group(1))
                    except:
                        continue
        return None
    
    def _find_transaction_id_in_row(self, row: List[str]) -> Optional[str]:
        """Find transaction ID in a row"""
        for cell in row:
            if not cell.strip():
                continue
            for pattern in self.transaction_id_patterns:
                match = re.search(pattern, cell)
                if match:
                    return match.group(0)
        return None
    
    def _find_transaction_id_in_line(self, line: str) -> Optional[str]:
        """Find transaction ID in a line"""
        for pattern in self.transaction_id_patterns:
            match = re.search(pattern, line)
            if match:
                return match.group(0)
        return None
    
    def _infer_transaction_type(self, data: List[str]) -> str:
        """Infer transaction type from data"""
        text = ' '.join(data).lower()
        
        if any(keyword in text for keyword in self.credit_keywords):
            return 'credit'
        elif any(keyword in text for keyword in self.debit_keywords):
            return 'debit'
        else:
            return 'debit'  # Default to debit
    
    def _deduplicate_transactions(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate transactions"""
        seen = set()
        unique_transactions = []
        
        for transaction in transactions:
            # Create unique key based on date, description, and amount
            key = (
                transaction['date'],
                transaction['description'].lower().strip(),
                transaction['amount']
            )
            
            if key not in seen:
                seen.add(key)
                unique_transactions.append(transaction)
        
        return unique_transactions 