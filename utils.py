import os
import pandas as pd
import numpy as np
from werkzeug.utils import secure_filename
import PyPDF2
from app import app, db
from models import FinancialData, Report
from ai_processor import process_with_gemini

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'pdf'}

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_csv(file_path):
    """Read and parse CSV file."""
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        app.logger.error(f"Error reading CSV file: {e}")
        return None

def read_excel(file_path):
    """Read and parse Excel file."""
    try:
        return pd.read_excel(file_path)
    except Exception as e:
        app.logger.error(f"Error reading Excel file: {e}")
        return None

def read_pdf(file_path):
    """Extract text from PDF file."""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        app.logger.error(f"Error reading PDF file: {e}")
        return None

def process_financial_data(file_id):
    """Process uploaded financial data file."""
    # Get file record
    financial_data = FinancialData.query.get(file_id)
    if not financial_data:
        app.logger.error(f"Financial data record with ID {file_id} not found")
        return False
    
    file_path = financial_data.file_path
    file_type = financial_data.file_type
    
    # Read file based on type
    data = None
    if file_type == 'csv':
        data = read_csv(file_path)
    elif file_type == 'xlsx':
        data = read_excel(file_path)
    elif file_type == 'pdf':
        data = read_pdf(file_path)
    
    if data is None:
        app.logger.error(f"Could not read file {file_path}")
        return False
    
    # Convert pandas DataFrame to JSON or leave as text for PDF
    if isinstance(data, pd.DataFrame):
        data_json = data.to_json(orient='records')
    else:
        data_json = data  # For PDF, data is already text
    
    # Process with AI to extract financial data structure
    try:
        processed_result = process_with_gemini(data_json, "extract_structure")
        
        # Update database record
        financial_data.processed = True
        db.session.commit()
        
        return True
    except Exception as e:
        app.logger.error(f"Error processing data with AI: {e}")
        return False

def generate_report(file_id, report_type):
    """Generate financial report for the given file."""
    # Get file record
    financial_data = FinancialData.query.get(file_id)
    if not financial_data:
        app.logger.error(f"Financial data record with ID {file_id} not found")
        raise ValueError("Financial data not found")
    
    file_path = financial_data.file_path
    file_type = financial_data.file_type
    
    # Read file based on type
    data = None
    if file_type == 'csv':
        data = read_csv(file_path)
    elif file_type == 'xlsx':
        data = read_excel(file_path)
    elif file_type == 'pdf':
        data = read_pdf(file_path)
    
    if data is None:
        app.logger.error(f"Could not read file {file_path}")
        raise ValueError("Could not read file")
    
    # Convert pandas DataFrame to JSON or leave as text for PDF
    if isinstance(data, pd.DataFrame):
        data_json = data.to_json(orient='records')
    else:
        data_json = data  # For PDF, data is already text
    
    # Process with AI to generate the specific report
    report_prompt = f"generate_{report_type}"
    try:
        report_content = process_with_gemini(data_json, report_prompt)
        return report_content
    except Exception as e:
        app.logger.error(f"Error generating report with AI: {e}")
        raise Exception(f"Error generating report: {str(e)}")

def format_currency(value):
    """Format number as currency."""
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return value

def calculate_percentage_change(old_value, new_value):
    """Calculate percentage change between two values."""
    try:
        old_value = float(old_value)
        new_value = float(new_value)
        if old_value == 0:
            return "N/A"
        change = ((new_value - old_value) / abs(old_value)) * 100
        return f"{change:.2f}%"
    except (ValueError, TypeError):
        return "N/A"

def detect_quarters(df):
    """
    Detect quarterly data in a DataFrame.
    Returns a list of column names or indices that represent quarters.
    """
    # Look for common quarter patterns in column names
    quarter_patterns = ['Q1', 'Q2', 'Q3', 'Q4', 'Quarter 1', 'Quarter 2', 'Quarter 3', 'Quarter 4']
    quarter_cols = []
    
    if isinstance(df, pd.DataFrame):
        for col in df.columns:
            col_str = str(col).upper()
            for pattern in quarter_patterns:
                if pattern.upper() in col_str:
                    quarter_cols.append(col)
                    break
    
    return quarter_cols
