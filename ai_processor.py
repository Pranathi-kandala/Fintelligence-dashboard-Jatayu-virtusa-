import os
import json
import pandas as pd
import numpy as np
import google.generativeai as genai
from datetime import datetime
import logging
import time
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('fintelligence')

# Configure the Gemini API
gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
if not gemini_api_key:
    logger.warning("GEMINI_API_KEY environment variable not set")

genai.configure(api_key=gemini_api_key)

# Set up the model with retry mechanism
# Using a "flash" model which has much higher rate limits than "pro"
# The model name must include the "models/" prefix for proper resolution
model = genai.GenerativeModel('models/gemini-1.5-flash')

# Maximum number of retries for API calls
MAX_RETRIES = 5

def ensure_response_structure(response_data, report_type):
    """
    Ensure AI response has proper structure expected by templates
    
    Args:
        response_data (dict): Raw data from AI
        report_type (str): Type of report (balance_sheet, income_statement, cash_flow, analysis)
        
    Returns:
        dict: Data with guaranteed structure
    """
    result = response_data.copy() if isinstance(response_data, dict) else {}
    
    # Common structure for fallback/error cases
    base_structure = {
        "error": None,
        "generated_at": datetime.now().isoformat(),
        "summary": "AI analysis results may be incomplete. Please try again later.",
        "insights": ["The financial data is currently being processed."],
        "recommendations": ["Consider refreshing or trying a different report."]
    }
    
    if report_type == "balance_sheet":
        # Ensure balance_sheet structure exists
        if "balance_sheet" not in result or not isinstance(result["balance_sheet"], dict):
            result["balance_sheet"] = {}
        
        # Ensure assets structure
        if "assets" not in result["balance_sheet"] or not isinstance(result["balance_sheet"]["assets"], dict):
            result["balance_sheet"]["assets"] = {"current_assets": [], "non_current_assets": []}
        elif "current_assets" not in result["balance_sheet"]["assets"]:
            result["balance_sheet"]["assets"]["current_assets"] = []
        elif "non_current_assets" not in result["balance_sheet"]["assets"]:
            result["balance_sheet"]["assets"]["non_current_assets"] = []
            
        # Ensure liabilities structure
        if "liabilities" not in result["balance_sheet"] or not isinstance(result["balance_sheet"]["liabilities"], dict):
            result["balance_sheet"]["liabilities"] = {"current_liabilities": [], "long_term_liabilities": []}
        elif "current_liabilities" not in result["balance_sheet"]["liabilities"]:
            result["balance_sheet"]["liabilities"]["current_liabilities"] = []
        elif "long_term_liabilities" not in result["balance_sheet"]["liabilities"]:
            result["balance_sheet"]["liabilities"]["long_term_liabilities"] = []
            
        # Ensure equity exists
        if "equity" not in result["balance_sheet"]:
            result["balance_sheet"]["equity"] = []
    
    elif report_type == "income_statement":
        # Ensure income_statement structure exists
        if "income_statement" not in result or not isinstance(result["income_statement"], dict):
            result["income_statement"] = {
                "revenue": 0,
                "cost_of_goods_sold": 0,
                "gross_profit": 0,
                "operating_expenses": [],
                "operating_income": 0,
                "other_income_expenses": [],
                "income_before_taxes": 0,
                "taxes": 0,
                "net_income": 0
            }
        
        # Add empty ratios if missing
        if "ratios" not in result:
            result["ratios"] = {}
    
    elif report_type == "cash_flow":
        # Ensure cash_flow structure exists
        if "cash_flow" not in result or not isinstance(result["cash_flow"], dict):
            result["cash_flow"] = {
                "operating_activities": [],
                "investing_activities": [],
                "financing_activities": [],
                "net_change": 0
            }
        
        # Ensure comparisons structure for charts
        if "comparisons" not in result or not isinstance(result["comparisons"], dict):
            result["comparisons"] = {
                "periods": ["Q1", "Q2", "Q3", "Q4"],
                "components": {
                    "operating_cash_flow": {"values": [0, 0, 0, 0], "trend": "stable"},
                    "investing_cash_flow": {"values": [0, 0, 0, 0], "trend": "stable"},
                    "financing_cash_flow": {"values": [0, 0, 0, 0], "trend": "stable"}
                }
            }
    
    elif report_type == "analysis":
        # Ensure analysis has all required sections
        for key in ["profitability", "liquidity", "efficiency", "solvency", "growth"]:
            if key not in result:
                result[key] = {"metrics": {}, "insights": []}
        
        # Ensure charts data exists
        if "charts_data" not in result:
            result["charts_data"] = {
                "revenue_trend": {"labels": [], "data": []},
                "expense_breakdown": {"labels": [], "data": []},
                "profit_margins": {"labels": [], "data": []}
            }
    
    # Apply base structure for missing fields
    for key, value in base_structure.items():
        if key not in result:
            result[key] = value
    
    return result

def optimize_data_for_tokens(file_data):
    """
    Optimize data for token usage to avoid rate limits
    
    Args:
        file_data (dict): Raw financial data from file processor
        
    Returns:
        str: Optimized data string for AI processing
    """
    # Convert file_data to string format with token optimization
    if file_data.get('format') == 'pdf':
        data_str = file_data.get('text', '')
        # Limit PDF text to reduce tokens
        if len(data_str) > 6000:
            logger.info(f"Reducing PDF data from {len(data_str)} to 6000 chars for token optimization")
            data_str = data_str[:6000] + "... [truncated for token optimization]"
    else:
        logger.debug("Processing CSV/Excel data with token optimization")
        # Safe data extraction with size limits
        data_list = []
        all_data = file_data.get('data', [])
        
        # Only use a sample of rows to stay within limits
        row_count = len(all_data)
        sample_size = min(30, row_count)  # Limit to 30 rows maximum
        
        if row_count > sample_size:
            logger.info(f"Sampling {sample_size} rows from {row_count} total rows for token optimization")
            # Take some rows from beginning, middle and end for a representative sample
            if sample_size >= 3:
                # Take 40% from start, 30% from middle, 30% from end
                start_count = int(sample_size * 0.4)
                mid_end_count = int(sample_size * 0.3)
                
                start_items = all_data[:start_count]
                middle_idx = row_count // 2
                middle_items = all_data[middle_idx:middle_idx + mid_end_count]
                end_items = all_data[-(mid_end_count):]
                
                sample_data = start_items + middle_items + end_items
            else:
                # If very small sample, just take from start
                sample_data = all_data[:sample_size]
        else:
            sample_data = all_data
            
        # Process the sampled data
        for item in sample_data:
            # Clean any potentially problematic characters
            clean_item = {}
            for key, value in item.items():
                if isinstance(value, str):
                    # Replace any characters that might cause parsing issues
                    clean_value = value.replace('\n', ' ').replace('\r', ' ')
                    # Limit string length for long text fields
                    if len(clean_value) > 100:
                        clean_value = clean_value[:100] + "..."
                    clean_item[key] = clean_value
                else:
                    clean_item[key] = value
            data_list.append(clean_item)
        
        # Convert to JSON with compact formatting to reduce tokens
        try:
            # Use compact JSON representation (no whitespace)
            data_str = json.dumps(data_list, separators=(',', ':'), default=str)
            # If still too large, truncate
            if len(data_str) > 8000:
                logger.info(f"Truncating JSON data from {len(data_str)} to 8000 chars for token optimization")
                data_str = data_str[:8000] + "... [truncated for token optimization]"
        except Exception as json_err:
            logger.error(f"Error converting data to JSON: {str(json_err)}")
            # Fallback to safer but still limited representation
            data_str = str(data_list[:15])
    
    return data_str

def call_gemini_with_retry(prompt):
    """
    Call Gemini API with retry logic for rate limits
    
    Args:
        prompt (str): The prompt text to send to the API
        
    Returns:
        response: The API response
    """
    # Debug log the API key configuration - hide sensitive data
    current_api_key = os.environ.get("GEMINI_API_KEY", "")
    if current_api_key:
        logger.info(f"Using Gemini API key: {current_api_key[:4]}...{current_api_key[-4:]} (length: {len(current_api_key)})")
    else:
        logger.error("No Gemini API key is configured!")
        
    # Update the configuration just to be sure we have the latest key
    genai.configure(api_key=current_api_key)
    
    retries = 0
    while retries < MAX_RETRIES:
        try:
            # Add small jitter to avoid thundering herd problem
            if retries > 0:
                jitter = random.uniform(1.0, 3.0)
                time.sleep(2**retries + jitter)  # Exponential backoff with jitter
                
            response = model.generate_content(prompt)
            return response
        except Exception as e:
            error_message = str(e)
            retries += 1
            
            logger.error(f"Gemini API error: {error_message}")
            
            if "quota" in error_message.lower() or "429" in error_message:
                # Specific handling for quota exceedance
                logger.warning(f"Rate limit or quota exceeded, retrying ({retries}/{MAX_RETRIES})...")
                # Extract retry delay if available in the error message
                if "retry_delay" in error_message and "seconds" in error_message:
                    try:
                        # Extract retry delay seconds from error
                        delay_text = error_message.split("retry_delay")[1]
                        seconds = int(delay_text.split("seconds")[0].strip("{").strip("}").strip(":").strip())
                        logger.info(f"Waiting for {seconds} seconds before retry...")
                        time.sleep(seconds + random.uniform(1.0, 5.0))  # Add jitter
                    except Exception as parse_err:
                        # Default delay if parsing fails
                        time.sleep(10 + random.uniform(1.0, 5.0))
                else:
                    # Default delay if no retry_delay in error
                    time.sleep(10 + random.uniform(1.0, 5.0))
            elif retries < MAX_RETRIES:
                # For other errors that aren't quota-related, still retry but with shorter delay
                logger.warning(f"Non-quota error, retrying ({retries}/{MAX_RETRIES})...")
                time.sleep(2 + random.uniform(0.5, 2.0))
            else:
                # If at max retries, just raise
                raise
                
    # If we've exhausted retries, raise the last error
    raise Exception(f"Failed to get response from Gemini API after {MAX_RETRIES} retries")

def generate_balance_sheet(file_data):
    """
    Generate a balance sheet from financial data using Gemini AI
    
    Args:
        file_data (dict): Processed financial data
        
    Returns:
        dict: Balance sheet data and insights
    """
    import logging
    logger = logging.getLogger('fintelligence')
    
    prompt = """
    Generate a detailed balance sheet based on the financial data provided.
    For the balance sheet, include:
    1. Assets (Current and Non-current)
    2. Liabilities (Current and Long-term)
    3. Equity
    
    Also provide the following:
    1. A summary of the financial position
    2. Key financial ratios (current ratio, debt-to-equity, etc.)
    3. Insights and recommendations based on the balance sheet
    
    Format your response as a JSON with the following structure:
    {
        "balance_sheet": {
            "assets": {
                "current_assets": [...],
                "non_current_assets": [...]
            },
            "liabilities": {
                "current_liabilities": [...],
                "long_term_liabilities": [...]
            },
            "equity": [...]
        },
        "summary": "...",
        "ratios": {...},
        "insights": [...],
        "recommendations": [...]
    }
    
    Here is the financial data:
    """
    
    try:
        # Convert file_data to string format for the prompt with safer handling
        if file_data.get('format') == 'pdf':
            data_str = file_data.get('text', '')
        else:
            logger.debug("Processing CSV/Excel data for AI")
            # Safe data extraction
            data_list = []
            for item in file_data.get('data', []):
                # Clean any potentially problematic characters
                clean_item = {}
                for key, value in item.items():
                    if isinstance(value, str):
                        # Replace any characters that might cause parsing issues
                        clean_value = value.replace('\n', ' ').replace('\r', ' ')
                        clean_item[key] = clean_value
                    else:
                        clean_item[key] = value
                data_list.append(clean_item)
            
            # Convert to JSON safely
            try:
                data_str = json.dumps(data_list, indent=2, default=str)
            except Exception as json_err:
                logger.error(f"Error converting data to JSON: {str(json_err)}")
                # Fallback to safer representation
                data_str = str(data_list)
        
        logger.debug("Preparing prompt for Gemini AI")
        full_prompt = prompt + "\n" + data_str
        
        # Call Gemini API with retry logic
        response = call_gemini_with_retry(full_prompt)
        
        # Extract JSON from response
        response_text = response.text
        logger.debug("Received response from Gemini AI")
        
        # Handle potential formatting issues in the response
        try:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx <= 0:
                logger.error("No valid JSON found in AI response")
                raise json.JSONDecodeError("No JSON found in response", response_text, 0)
                
            json_str = response_text[start_idx:end_idx]
            result = json.loads(json_str)
        except json.JSONDecodeError as json_err:
            logger.error(f"JSON parse error: {str(json_err)}")
            # Fallback if JSON parsing fails
            result = {
                "balance_sheet": {
                    "error": "Failed to parse AI response. Please try again."
                },
                "raw_response": response_text[:500]  # Truncate for safety
            }
        
        # Add generation metadata
        result["generated_at"] = datetime.now().isoformat()
        result["source_format"] = file_data.get('format')
        
        # Ensure proper structure for template rendering
        result = ensure_response_structure(result, "balance_sheet")
        
        return result
    
    except Exception as e:
        import traceback
        logger.error(f"Balance sheet generation error: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "error": f"Failed to generate balance sheet: {str(e)}",
            "generated_at": datetime.now().isoformat()
        }

def fix_json_content(response_text):
    """
    Try to extract valid JSON from response text
    
    Args:
        response_text (str): Raw response text from API
        
    Returns:
        dict: Parsed JSON or error dict
    """
    try:
        # Find and extract JSON content
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx == -1 or end_idx <= 0:
            logger.error("No valid JSON found in AI response")
            raise json.JSONDecodeError("No JSON found in response", response_text, 0)
            
        json_str = response_text[start_idx:end_idx]
        return json.loads(json_str)
    except json.JSONDecodeError as json_err:
        logger.error(f"JSON parse error: {str(json_err)}")
        return {
            "error": "Failed to parse AI response. Please try again.",
            "raw_response": response_text[:500]  # Truncate for safety
        }

def process_ai_response(response_text, report_type, file_data):
    """
    Process AI response with proper error handling and structure validation
    
    Args:
        response_text (str): Raw response text from API
        report_type (str): Type of report to validate (balance_sheet, income_statement, etc.)
        file_data (dict): Original data processed
        
    Returns:
        dict: Structured and validated response
    """
    # Extract JSON from response
    logger.debug("Processing AI response")
    
    # Parse JSON content with error handling
    result = fix_json_content(response_text)
    
    # Add generation metadata
    result["generated_at"] = datetime.now().isoformat()
    result["source_format"] = file_data.get('format')
    
    # Ensure proper structure for template rendering
    result = ensure_response_structure(result, report_type)
    
    return result

def generate_income_statement(file_data):
    """
    Generate an income statement from financial data using Gemini AI
    
    Args:
        file_data (dict): Processed financial data
        
    Returns:
        dict: Income statement data and insights
    """
    import logging
    logger = logging.getLogger('fintelligence')
    
    prompt = """
    Generate a detailed income statement based on the financial data provided.
    For the income statement, include:
    1. Revenue (broken down by sources if available)
    2. Cost of Goods Sold
    3. Gross Profit
    4. Operating Expenses
    5. Operating Income
    6. Other Income/Expenses
    7. Net Income before Tax
    8. Taxes
    9. Net Income
    
    Also provide the following:
    1. A summary of the financial performance
    2. Key profitability ratios (gross profit margin, net profit margin, etc.)
    3. Insights and recommendations based on the income statement
    4. Quarter-over-quarter or year-over-year comparisons if data is available
    
    Format your response as a JSON with the following structure:
    {
        "income_statement": {
            "revenue": {...},
            "cogs": {...},
            "gross_profit": {...},
            "operating_expenses": {...},
            "operating_income": {...},
            "other_income_expenses": {...},
            "net_income_before_tax": {...},
            "taxes": {...},
            "net_income": {...}
        },
        "summary": "...",
        "ratios": {...},
        "insights": [...],
        "recommendations": [...],
        "comparisons": {...}
    }
    
    Here is the financial data:
    """
    
    try:
        # Use token-optimized data preparation
        data_str = optimize_data_for_tokens(file_data)
        
        logger.debug("Preparing prompt for Gemini AI")
        full_prompt = prompt + "\n" + data_str
        
        # Call Gemini API with retry logic
        response = call_gemini_with_retry(full_prompt)
        
        # Process the response with our common function
        result = process_ai_response(response.text, "income_statement", file_data)
        
        return result
    
    except Exception as e:
        import traceback
        logger.error(f"Income statement generation error: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "error": f"Failed to generate income statement: {str(e)}",
            "generated_at": datetime.now().isoformat()
        }

def generate_cash_flow(file_data):
    """
    Generate a cash flow statement from financial data using Gemini AI
    
    Args:
        file_data (dict): Processed financial data
        
    Returns:
        dict: Cash flow statement data and insights
    """
    import logging
    logger = logging.getLogger('fintelligence')
    
    prompt = """
    Generate a detailed cash flow statement based on the financial data provided.
    For the cash flow statement, include:
    1. Operating Activities
    2. Investing Activities
    3. Financing Activities
    4. Net Change in Cash
    
    Also provide the following:
    1. A summary of the cash flow position
    2. Key cash flow ratios and metrics
    3. Insights and recommendations based on the cash flow statement
    4. Period-over-period comparisons if data is available
    
    Format your response as a JSON with the following structure:
    {
        "cash_flow_statement": {
            "operating_activities": [...],
            "investing_activities": [...],
            "financing_activities": [...],
            "net_change_in_cash": {...}
        },
        "summary": "...",
        "metrics": {...},
        "insights": [...],
        "recommendations": [...],
        "comparisons": {...}
    }
    
    Here is the financial data:
    """
    
    try:
        # Convert file_data to string format for the prompt with safer handling
        if file_data.get('format') == 'pdf':
            data_str = file_data.get('text', '')
        else:
            logger.debug("Processing CSV/Excel data for AI")
            # Safe data extraction
            data_list = []
            for item in file_data.get('data', []):
                # Clean any potentially problematic characters
                clean_item = {}
                for key, value in item.items():
                    if isinstance(value, str):
                        # Replace any characters that might cause parsing issues
                        clean_value = value.replace('\n', ' ').replace('\r', ' ')
                        clean_item[key] = clean_value
                    else:
                        clean_item[key] = value
                data_list.append(clean_item)
            
            # Convert to JSON safely
            try:
                data_str = json.dumps(data_list, indent=2, default=str)
            except Exception as json_err:
                logger.error(f"Error converting data to JSON: {str(json_err)}")
                # Fallback to safer representation
                data_str = str(data_list)
        
        logger.debug("Preparing prompt for Gemini AI")
        full_prompt = prompt + "\n" + data_str
        
        # Call Gemini API with retry logic
        response = call_gemini_with_retry(full_prompt)
        
        # Extract JSON from response
        response_text = response.text
        logger.debug("Received response from Gemini AI")
        
        # Handle potential formatting issues in the response
        try:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx <= 0:
                logger.error("No valid JSON found in AI response")
                raise json.JSONDecodeError("No JSON found in response", response_text, 0)
                
            json_str = response_text[start_idx:end_idx]
            result = json.loads(json_str)
            
            # Verify key fields exist in the response
            if "cash_flow_statement" not in result:
                logger.warning("Cash flow statement data missing from response")
                result["cash_flow_statement"] = {
                    "error": "Cash flow data missing from AI response"
                }
        except json.JSONDecodeError as json_err:
            logger.error(f"JSON parse error: {str(json_err)}")
            # Fallback if JSON parsing fails
            result = {
                "cash_flow_statement": {
                    "error": "Failed to parse AI response. Please try again."
                },
                "raw_response": response_text[:500]  # Truncate for safety
            }
        
        # Add generation metadata
        result["generated_at"] = datetime.now().isoformat()
        result["source_format"] = file_data.get('format')
        
        return result
    
    except Exception as e:
        import traceback
        logger.error(f"Cash flow generation error: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "error": f"Failed to generate cash flow statement: {str(e)}",
            "generated_at": datetime.now().isoformat()
        }

def generate_analysis(file_data):
    """
    Generate a comprehensive financial analysis from financial data using Gemini AI
    
    Args:
        file_data (dict): Processed financial data
        
    Returns:
        dict: Financial analysis data and insights
    """
    import logging
    logger = logging.getLogger('fintelligence')
    
    prompt = """
    Generate a comprehensive financial analysis based on the provided financial data. Include the following components:
    
    1. Overall Financial Health Assessment
    2. Trend Analysis across quarters/periods
    3. Key Performance Indicators (KPIs)
    4. Profitability Analysis
    5. Liquidity Analysis
    6. Solvency Analysis
    7. Efficiency/Activity Analysis
    8. Top Expenses Analysis
    9. Revenue Breakdown
    10. Strategic Recommendations
    
    Format your response as a JSON with the following structure:
    {
       "financial_health": {
         "summary": "...",
         "rating": "...",
         "key_strengths": [...],
         "key_weaknesses": [...]
       },
       "trend_analysis": {
         "revenue_trend": {
           "summary": "...",
           "quarterly_growth_rates": [...],
           "trend_direction": "..."
         },
         "expense_trend": {
           "summary": "...",
           "quarterly_growth_rates": [...],
           "trend_direction": "..."
         },
         "profit_trend": {
           "summary": "...",
           "quarterly_growth_rates": [...],
           "trend_direction": "..."
         }
       },
       "key_performance_indicators": {
         "current_period": {...},
         "previous_period": {...},
         "industry_benchmarks": {...}
       },
       "profitability_analysis": {
         "summary": "...",
         "metrics": {...}
       },
       "liquidity_analysis": {
         "summary": "...",
         "metrics": {...}
       },
       "solvency_analysis": {
         "summary": "...",
         "metrics": {...}
       },
       "efficiency_analysis": {
         "summary": "...",
         "metrics": {...}
       },
       "expense_analysis": {
         "summary": "...",
         "top_expenses": [...],
         "expense_categories": {...}
       },
       "revenue_analysis": {
         "summary": "...",
         "revenue_sources": [...],
         "revenue_concentration": "..."
       },
       "recommendations": [
         {
           "area": "...",
           "recommendation": "...",
           "impact": "...",
           "implementation_difficulty": "..."
         },
         ...
       ],
       "financial_charts_data": {
         "revenue_by_quarter": {
           "labels": ["Q1", "Q2", "Q3", "Q4"],
           "values": [...]
         },
         "expenses_by_quarter": {
           "labels": ["Q1", "Q2", "Q3", "Q4"],
           "values": [...]
         },
         "profit_by_quarter": {
           "labels": ["Q1", "Q2", "Q3", "Q4"],
           "values": [...]
         },
         "expense_breakdown": {
           "labels": [...],
           "values": [...]
         },
         "revenue_breakdown": {
           "labels": [...],
           "values": [...]
         }
       },
       "financial_ratios": {
         "Current Ratio": [1.8, 1.9, 2.0, 2.1],
         "Debt-to-Equity": [0.8, 0.75, 0.7, 0.65]
       }
    
    CRITICAL: These data structures MUST be based on the actual data provided, not invented or fabricated values.
    All values must be calculated from the financial data provided.
    
    Format your entire response as valid JSON with these exact structures to enable chart generation.
    
    Here is the financial data:
    """
    
    try:
        # Convert file_data to string format for the prompt with safer handling
        if file_data.get('format') == 'pdf':
            data_str = file_data.get('text', '')
        else:
            logger.debug("Processing CSV/Excel data for financial analysis")
            # Safe data extraction
            data_list = []
            for item in file_data.get('data', []):
                # Clean any potentially problematic characters
                clean_item = {}
                for key, value in item.items():
                    if isinstance(value, str):
                        # Replace any characters that might cause parsing issues
                        clean_value = value.replace('\n', ' ').replace('\r', ' ')
                        clean_item[key] = clean_value
                    else:
                        clean_item[key] = value
                data_list.append(clean_item)
            
            # Convert to JSON safely
            try:
                data_str = json.dumps(data_list, indent=2, default=str)
            except Exception as json_err:
                logger.error(f"Error converting data to JSON: {str(json_err)}")
                # Fallback to safer representation
                data_str = str(data_list)
        
        logger.debug("Preparing prompt for Gemini AI")
        full_prompt = prompt + "\n" + data_str
        
        # Call Gemini API with retry logic
        response = call_gemini_with_retry(full_prompt)
        
        # Extract JSON from response
        response_text = response.text
        logger.debug("Received response from Gemini AI")
        
        # Handle potential formatting issues in the response
        try:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx <= 0:
                logger.error("No valid JSON found in AI response")
                raise json.JSONDecodeError("No JSON found in response", response_text, 0)
                
            json_str = response_text[start_idx:end_idx]
            result = json.loads(json_str)
        except json.JSONDecodeError as json_err:
            logger.error(f"JSON parse error: {str(json_err)}")
            # Fallback if JSON parsing fails
            result = {
                "financial_analysis": {
                    "error": "Failed to parse AI response. Please try again."
                },
                "raw_response": response_text[:500]  # Truncate for safety
            }
        
        # Add generation metadata
        result["generated_at"] = datetime.now().isoformat()
        result["source_format"] = file_data.get('format')
        
        return result
    
    except Exception as e:
        import traceback
        logger.error(f"Financial analysis generation error: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "error": f"Failed to generate financial analysis: {str(e)}",
            "generated_at": datetime.now().isoformat()
        }

def process_chat_query(user_query, file_data):
    """
    Process a user query about financial data using Gemini AI
    
    Args:
        user_query (str): User's financial question
        file_data (list): List of dictionaries containing file data and reports
        
    Returns:
        str: AI response to user query
    """
    import logging
    logger = logging.getLogger('fintelligence')
    
    prompt = f"""
    You are a financial analyst AI assistant. Answer the following question based on the provided financial data and reports.
    Provide detailed, accurate, and helpful financial insights.
    
    USER QUESTION: {user_query}
    
    Here is the financial data and previously generated reports:
    """
    
    try:
        # Prepare the financial data context
        data_context = []
        
        # First, add the raw financial data
        if isinstance(file_data, list) and len(file_data) > 0:
            for item in file_data:
                # Add raw data if available
                if 'data' in item and item['data']:
                    data_subset = []
                    # Limit to first 20 records to avoid context size issues
                    for record in item['data'][:20]:
                        data_subset.append(record)
                    data_context.append({"raw_data": data_subset})
                
                # Add reports if available
                for report_type in ['balance_sheet', 'income_statement', 'cash_flow', 'analysis']:
                    report_key = f"{report_type}_report"
                    if report_key in item and item[report_key]:
                        data_context.append({f"{report_type}": item[report_key]})
        
        # Convert to JSON for the prompt
        data_str = json.dumps(data_context, indent=2, default=str)
        full_prompt = prompt + "\n" + data_str
        
        # Call Gemini API with retry logic
        response = call_gemini_with_retry(full_prompt)
        
        # Return the text response directly
        return response.text
    
    except Exception as e:
        logger.error(f"Chat query processing error: {str(e)}")
        return f"I'm sorry, I encountered an error while processing your question: {str(e)}"

def explain_ai_decision(report_type, report_data):
    """
    Generate an explanation of how the AI reached its conclusions for a report
    
    Args:
        report_type (str): Type of report (balance_sheet, income_statement, cash_flow, analysis)
        report_data (dict): Report data generated by the AI
        
    Returns:
        dict: Explanation of AI decision process
    """
    import logging
    logger = logging.getLogger('fintelligence')
    
    prompt = f"""
    You are a financial explainability expert. Given the following {report_type} report generated by an AI system,
    explain how the AI likely reached these conclusions, what data points it analyzed, and what methodologies it likely used.
    Provide insights into the reasoning behind the analyses, calculations, and recommendations.
    
    Format your response as a JSON with the following structure:
    {{
        "methodology": "Description of the analytical approach used",
        "key_data_points": ["Data point 1", "Data point 2", ...],
        "calculation_explanations": {{
            "calculation1": "Explanation of how this was calculated",
            "calculation2": "Explanation of how this was calculated",
            ...
        }},
        "decision_factors": ["Factor 1", "Factor 2", ...],
        "confidence_assessment": "Assessment of how confident the AI should be in these conclusions",
        "limitations": ["Limitation 1", "Limitation 2", ...]
    }}
    
    Here is the {report_type} report:
    """
    
    try:
        # Convert report data to JSON for the prompt
        report_json = json.dumps(report_data, indent=2, default=str)
        full_prompt = prompt + "\n" + report_json
        
        # Call Gemini API with retry logic
        response = call_gemini_with_retry(full_prompt)
        
        # Extract JSON from response
        response_text = response.text
        
        # Handle potential formatting issues in the response
        try:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx <= 0:
                logger.error("No valid JSON found in AI explanation response")
                raise json.JSONDecodeError("No JSON found in response", response_text, 0)
                
            json_str = response_text[start_idx:end_idx]
            result = json.loads(json_str)
            
            # Add metadata
            result["generated_at"] = datetime.now().isoformat()
            
            return result
        except json.JSONDecodeError as json_err:
            logger.error(f"JSON parse error in explanation: {str(json_err)}")
            # Fallback if JSON parsing fails
            return {
                "error": "Failed to parse AI explanation response.",
                "methodology": "Unable to determine due to parsing error",
                "raw_response": response_text[:500],  # Truncate for safety
                "generated_at": datetime.now().isoformat()
            }
    
    except Exception as e:
        logger.error(f"Explanation generation error: {str(e)}")
        return {
            "error": f"Failed to generate explanation: {str(e)}",
            "generated_at": datetime.now().isoformat()
        }