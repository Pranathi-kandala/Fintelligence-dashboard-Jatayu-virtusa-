import pandas as pd
import numpy as np
import io
import csv
import json
import PyPDF2

def process_uploaded_file(file_path, file_type):
    """
    Process an uploaded financial data file
    
    Args:
        file_path (str): Path to the uploaded file
        file_type (str): File extension (csv, xlsx, pdf)
        
    Returns:
        dict: Extracted and structured financial data
    """
    try:
        if file_type == 'csv':
            return process_csv(file_path)
        elif file_type == 'xlsx':
            return process_xlsx(file_path)
        elif file_type == 'pdf':
            return process_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    except Exception as e:
        raise Exception(f"Error processing file: {str(e)}")

def process_csv(file_path):
    """Process CSV financial data file"""
    try:
        # Read CSV file
        df = pd.read_csv(file_path)
        
        # Basic validation
        if df.empty:
            raise ValueError("CSV file is empty")
        
        # Convert DataFrame to dict
        data = df.to_dict(orient='records')
        
        # Extract column names
        columns = df.columns.tolist()
        
        return {
            'data': data,
            'columns': columns,
            'format': 'csv',
            'rows': len(data)
        }
    except Exception as e:
        raise Exception(f"Error processing CSV file: {str(e)}")

def process_xlsx(file_path):
    """Process Excel financial data file"""
    try:
        # Read Excel file (first sheet by default)
        df = pd.read_excel(file_path)
        
        # Basic validation
        if df.empty:
            raise ValueError("Excel file is empty")
        
        # Convert DataFrame to dict
        data = df.to_dict(orient='records')
        
        # Extract column names
        columns = df.columns.tolist()
        
        # Check if there are multiple sheets
        xl = pd.ExcelFile(file_path)
        sheets = xl.sheet_names
        
        sheet_data = {}
        if len(sheets) > 1:
            for sheet in sheets:
                sheet_df = pd.read_excel(file_path, sheet_name=sheet)
                sheet_data[sheet] = sheet_df.to_dict(orient='records')
        
        result = {
            'data': data,
            'columns': columns,
            'format': 'xlsx',
            'rows': len(data),
            'sheets': sheets
        }
        
        if sheet_data:
            result['sheet_data'] = sheet_data
            
        return result
        
    except Exception as e:
        raise Exception(f"Error processing Excel file: {str(e)}")

def process_pdf(file_path):
    """
    Process PDF financial data file
    This function attempts to extract tabular data from PDF
    """
    try:
        # Open the PDF file
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            
            if num_pages == 0:
                raise ValueError("PDF file is empty")
            
            # Extract text from each page
            extracted_text = []
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                extracted_text.append(text)
            
            # Join all text
            full_text = "\n".join(extracted_text)
            
            # Basic structure for the extracted data
            result = {
                'format': 'pdf',
                'pages': num_pages,
                'text': full_text,
                'raw_content': True
            }
            
            return result
            
    except Exception as e:
        raise Exception(f"Error processing PDF file: {str(e)}")
