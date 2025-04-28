import io
import os
import pytz
from datetime import datetime
from xhtml2pdf import pisa

def convert_html_to_pdf(html_content):
    """
    Convert HTML content to PDF
    
    Args:
        html_content (str): HTML content to convert
        
    Returns:
        BytesIO: PDF file as BytesIO object
    """
    pdf_io = io.BytesIO()
    
    # Convert HTML to PDF
    pisa_status = pisa.CreatePDF(
        html_content,
        dest=pdf_io
    )
    
    # Return PDF file if successful
    if pisa_status.err:
        return None
    
    pdf_io.seek(0)
    return pdf_io

def get_current_ist_time():
    """
    Get current time in Indian Standard Time (IST)
    
    Returns:
        datetime: Current time in IST
    """
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)

def format_ist_time(dt=None, format_str='%Y-%m-%d %H:%M:%S %Z'):
    """
    Format datetime in Indian Standard Time (IST)
    
    Args:
        dt (datetime, optional): Datetime to format. Defaults to current time.
        format_str (str, optional): Format string. Defaults to '%Y-%m-%d %H:%M:%S %Z'.
        
    Returns:
        str: Formatted datetime string in IST
    """
    if dt is None:
        dt = get_current_ist_time()
    
    # If datetime is naive (no timezone), assign IST
    if dt.tzinfo is None:
        ist = pytz.timezone('Asia/Kolkata')
        dt = ist.localize(dt)
    # If datetime has timezone but not IST, convert to IST
    elif dt.tzinfo != pytz.timezone('Asia/Kolkata'):
        ist = pytz.timezone('Asia/Kolkata')
        dt = dt.astimezone(ist)
        
    return dt.strftime(format_str)