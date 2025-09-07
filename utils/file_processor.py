#!/usr/bin/env python3
"""
File upload and processing utilities with OCR support
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

try:
    import cv2
    import numpy as np
    from PIL import Image
    import pytesseract
    from PyPDF2 import PdfReader
    import pandas as pd
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

from .formatting import extract_amount_from_text, parse_indian_amount

logger = logging.getLogger(__name__)


class FileProcessor:
    """Handle file upload and processing with OCR capabilities"""
    
    ALLOWED_EXTENSIONS = {
        'images': {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'},
        'documents': {'.pdf', '.txt', '.doc', '.docx'},
        'spreadsheets': {'.csv', '.xlsx', '.xls'},
        'data': {'.json', '.xml', '.log'}
    }
    
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    
    def __init__(self, upload_dir: str):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for different file types
        for file_type in self.ALLOWED_EXTENSIONS.keys():
            (self.upload_dir / file_type).mkdir(exist_ok=True)
    
    def is_allowed_file(self, filename: str) -> tuple:
        """Check if file extension is allowed"""
        if not filename:
            return False, "No filename provided"
        
        file_ext = Path(filename).suffix.lower()
        
        for file_type, extensions in self.ALLOWED_EXTENSIONS.items():
            if file_ext in extensions:
                return True, file_type
        
        return False, "File type not supported"
    
    def save_uploaded_file(self, file, filename: str) -> Dict[str, Any]:
        """Save uploaded file and return file info"""
        try:
            # Check file size
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > self.MAX_FILE_SIZE:
                return {
                    'success': False,
                    'error': f'File too large. Maximum size: {self.MAX_FILE_SIZE // (1024*1024)}MB'
                }
            
            # Check file type
            allowed, file_type = self.is_allowed_file(filename)
            if not allowed:
                return {
                    'success': False,
                    'error': f'File type not supported: {file_type}'
                }
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{timestamp}_{filename}"
            file_path = self.upload_dir / file_type / safe_filename
            
            # Save file
            file.save(str(file_path))
            
            return {
                'success': True,
                'file_path': str(file_path),
                'file_type': file_type,
                'file_size': file_size,
                'original_filename': filename,
                'saved_filename': safe_filename,
                'upload_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            return {
                'success': False,
                'error': f'Error saving file: {str(e)}'
            }
    
    def process_file(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Process uploaded file and extract relevant data"""
        try:
            if file_type == 'images':
                return self.process_image(file_path)
            elif file_type == 'documents':
                return self.process_document(file_path)
            elif file_type == 'spreadsheets':
                return self.process_spreadsheet(file_path)
            elif file_type == 'data':
                return self.process_data_file(file_path)
            else:
                return {
                    'success': False,
                    'error': f'Unknown file type: {file_type}'
                }
        
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            return {
                'success': False,
                'error': f'Error processing file: {str(e)}'
            }
    
    def process_image(self, file_path: str) -> Dict[str, Any]:
        """Process image file with OCR"""
        if not OCR_AVAILABLE:
            return {
                'success': False,
                'error': 'OCR libraries not available. Please install pytesseract and opencv-python.'
            }
        
        try:
            # Read image
            image = cv2.imread(file_path)
            if image is None:
                return {
                    'success': False,
                    'error': 'Could not read image file'
                }
            
            # Preprocess image for better OCR
            processed_image = self.preprocess_image(image)
            
            # Extract text using OCR
            extracted_text = pytesseract.image_to_string(processed_image)
            
            # Extract financial data
            financial_data = self.extract_financial_data(extracted_text)
            
            return {
                'success': True,
                'extracted_text': extracted_text,
                'financial_data': financial_data,
                'file_type': 'image',
                'processing_method': 'OCR'
            }
            
        except Exception as e:
            logger.error(f"Error processing image {file_path}: {str(e)}")
            return {
                'success': False,
                'error': f'Error processing image: {str(e)}'
            }
    
    def preprocess_image(self, image):
        """Preprocess image for better OCR results"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply denoising
        denoised = cv2.medianBlur(gray, 5)
        
        # Apply thresholding
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Dilation and erosion to clean up the image
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return processed
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process PDF or text documents"""
        try:
            file_ext = Path(file_path).suffix.lower()
            extracted_text = ""
            
            if file_ext == '.pdf':
                # Extract text from PDF
                with open(file_path, 'rb') as file:
                    reader = PdfReader(file)
                    for page in reader.pages:
                        extracted_text += page.extract_text() + "\n"
            
            elif file_ext == '.txt':
                # Read text file
                with open(file_path, 'r', encoding='utf-8') as file:
                    extracted_text = file.read()
            
            else:
                return {
                    'success': False,
                    'error': f'Document type {file_ext} not supported yet'
                }
            
            # Extract financial data
            financial_data = self.extract_financial_data(extracted_text)
            
            return {
                'success': True,
                'extracted_text': extracted_text,
                'financial_data': financial_data,
                'file_type': 'document',
                'processing_method': 'text_extraction'
            }
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            return {
                'success': False,
                'error': f'Error processing document: {str(e)}'
            }
    
    def process_spreadsheet(self, file_path: str) -> Dict[str, Any]:
        """Process CSV or Excel files"""
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                return {
                    'success': False,
                    'error': f'Spreadsheet type {file_ext} not supported'
                }
            
            # Extract financial data from dataframe
            financial_data = self.extract_financial_data_from_dataframe(df)
            
            return {
                'success': True,
                'dataframe_info': {
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': list(df.columns)
                },
                'sample_data': df.head().to_dict('records'),
                'financial_data': financial_data,
                'file_type': 'spreadsheet',
                'processing_method': 'dataframe_analysis'
            }
            
        except Exception as e:
            logger.error(f"Error processing spreadsheet {file_path}: {str(e)}")
            return {
                'success': False,
                'error': f'Error processing spreadsheet: {str(e)}'
            }
    
    def process_data_file(self, file_path: str) -> Dict[str, Any]:
        """Process JSON, XML, or log files"""
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                
                # Extract financial data from JSON
                financial_data = self.extract_financial_data_from_json(data)
                
                return {
                    'success': True,
                    'json_data': data,
                    'financial_data': financial_data,
                    'file_type': 'json',
                    'processing_method': 'json_parsing'
                }
            
            elif file_ext == '.log':
                with open(file_path, 'r', encoding='utf-8') as file:
                    log_content = file.read()
                
                # Extract financial data from logs
                financial_data = self.extract_financial_data(log_content)
                
                return {
                    'success': True,
                    'log_content': log_content[:1000] + "..." if len(log_content) > 1000 else log_content,
                    'financial_data': financial_data,
                    'file_type': 'log',
                    'processing_method': 'log_parsing'
                }
            
            else:
                return {
                    'success': False,
                    'error': f'Data file type {file_ext} not supported yet'
                }
                
        except Exception as e:
            logger.error(f"Error processing data file {file_path}: {str(e)}")
            return {
                'success': False,
                'error': f'Error processing data file: {str(e)}'
            }
    
    def extract_financial_data(self, text: str) -> Dict[str, Any]:
        """Extract financial information from text"""
        financial_data = {
            'amounts': [],
            'invoice_numbers': [],
            'dates': [],
            'customer_info': [],
            'service_types': [],
            'billing_info': {}
        }
        
        try:
            # Extract amounts
            amounts = extract_amount_from_text(text)
            financial_data['amounts'] = amounts
            
            # Extract invoice/bill numbers
            invoice_patterns = [
                r'invoice[#\s]*:?\s*([A-Z0-9-]+)',
                r'bill[#\s]*:?\s*([A-Z0-9-]+)',
                r'receipt[#\s]*:?\s*([A-Z0-9-]+)',
            ]
            
            for pattern in invoice_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                financial_data['invoice_numbers'].extend(matches)
            
            # Extract dates
            date_patterns = [
                r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
                r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}',
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                financial_data['dates'].extend(matches)
            
            # Extract customer information
            customer_patterns = [
                r'customer[#\s]*:?\s*([A-Z0-9-]+)',
                r'account[#\s]*:?\s*([A-Z0-9-]+)',
                r'client[#\s]*:?\s*([A-Z0-9-]+)',
            ]
            
            for pattern in customer_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                financial_data['customer_info'].extend(matches)
            
            # Extract service types (common telecom/utility services)
            service_patterns = [
                r'(voice|data|sms|internet|electricity|gas|water)',
                r'(prepaid|postpaid|broadband|mobile)',
            ]
            
            for pattern in service_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                financial_data['service_types'].extend(matches)
            
            # Calculate summary
            if amounts:
                financial_data['billing_info'] = {
                    'total_amount': sum(amounts),
                    'max_amount': max(amounts),
                    'min_amount': min(amounts),
                    'amount_count': len(amounts)
                }
            
        except Exception as e:
            logger.error(f"Error extracting financial data: {str(e)}")
            financial_data['extraction_error'] = str(e)
        
        return financial_data
    
    def extract_financial_data_from_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract financial data from pandas DataFrame"""
        financial_data = {
            'amount_columns': [],
            'date_columns': [],
            'id_columns': [],
            'summary': {}
        }
        
        try:
            # Identify potential amount columns
            amount_keywords = ['amount', 'price', 'cost', 'fee', 'charge', 'bill', 'total', 'balance']
            for col in df.columns:
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in amount_keywords):
                    if pd.api.types.is_numeric_dtype(df[col]):
                        financial_data['amount_columns'].append(col)
            
            # Identify date columns
            date_keywords = ['date', 'time', 'created', 'updated', 'bill_date', 'due_date']
            for col in df.columns:
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in date_keywords):
                    financial_data['date_columns'].append(col)
            
            # Identify ID columns
            id_keywords = ['id', 'number', 'code', 'ref', 'invoice', 'customer', 'account']
            for col in df.columns:
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in id_keywords):
                    financial_data['id_columns'].append(col)
            
            # Calculate summary for amount columns
            if financial_data['amount_columns']:
                summary = {}
                for col in financial_data['amount_columns']:
                    summary[col] = {
                        'total': float(df[col].sum()),
                        'mean': float(df[col].mean()),
                        'max': float(df[col].max()),
                        'min': float(df[col].min()),
                        'count': int(df[col].count())
                    }
                financial_data['summary'] = summary
            
        except Exception as e:
            logger.error(f"Error extracting financial data from dataframe: {str(e)}")
            financial_data['extraction_error'] = str(e)
        
        return financial_data
    
    def extract_financial_data_from_json(self, data: Any) -> Dict[str, Any]:
        """Extract financial data from JSON data"""
        financial_data = {
            'found_amounts': [],
            'found_keys': [],
            'structure_info': {}
        }
        
        try:
            # Recursively search for financial data
            self._search_json_for_financial_data(data, financial_data)
            
            # Analyze structure
            if isinstance(data, dict):
                financial_data['structure_info'] = {
                    'type': 'object',
                    'keys': list(data.keys())[:10],  # First 10 keys
                    'total_keys': len(data.keys())
                }
            elif isinstance(data, list):
                financial_data['structure_info'] = {
                    'type': 'array',
                    'length': len(data),
                    'sample_item': data[0] if data else None
                }
            
        except Exception as e:
            logger.error(f"Error extracting financial data from JSON: {str(e)}")
            financial_data['extraction_error'] = str(e)
        
        return financial_data
    
    def _search_json_for_financial_data(self, obj: Any, result: Dict, path: str = ""):
        """Recursively search JSON for financial data"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                
                # Check if key suggests financial data
                key_lower = key.lower()
                if any(keyword in key_lower for keyword in ['amount', 'price', 'cost', 'fee', 'total', 'balance']):
                    result['found_keys'].append(new_path)
                    if isinstance(value, (int, float)):
                        result['found_amounts'].append(value)
                
                # Recurse into nested structures
                self._search_json_for_financial_data(value, result, new_path)
        
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_path = f"{path}[{i}]"
                self._search_json_for_financial_data(item, result, new_path)
        
        elif isinstance(obj, (int, float)) and obj > 0:
            # Potential amount value
            result['found_amounts'].append(obj)


def create_sample_upload_data(processor: FileProcessor) -> Dict[str, Any]:
    """Create sample data for testing file uploads"""
    try:
        sample_data = {
            'sample_bill_data': {
                'invoice_number': 'INV-2024-001',
                'customer_id': 'CUST-12345',
                'bill_date': '2024-01-15',
                'due_date': '2024-02-15',
                'services': [
                    {
                        'service_type': 'Voice',
                        'usage': '450 minutes',
                        'rate': '₹1.20 per minute',
                        'amount': 540.00
                    },
                    {
                        'service_type': 'Data',
                        'usage': '12 GB',
                        'rate': '₹150 per GB',
                        'amount': 1800.00
                    },
                    {
                        'service_type': 'SMS',
                        'usage': '200 messages',
                        'rate': '₹0.50 per SMS',
                        'amount': 100.00
                    }
                ],
                'subtotal': 2440.00,
                'tax': 439.20,
                'total_amount': 2879.20
            },
            'supported_formats': {
                'images': ['JPEG', 'PNG', 'PDF scans', 'TIFF'],
                'documents': ['PDF', 'TXT', 'DOC', 'DOCX'],
                'spreadsheets': ['CSV', 'XLSX', 'XLS'],
                'data_files': ['JSON', 'XML', 'LOG files']
            },
            'processing_capabilities': [
                'OCR text extraction from images',
                'PDF text extraction',
                'Automatic amount detection',
                'Invoice/bill number extraction',
                'Date extraction',
                'Customer information parsing',
                'Service type identification'
            ]
        }
        
        return sample_data
        
    except Exception as e:
        logger.error(f"Error creating sample upload data: {str(e)}")
        return {'error': str(e)}
