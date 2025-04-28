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
# Use the stable release to avoid breaking changes
model = genai.GenerativeModel('gemini-1.5-pro')

# Maximum number of retries for API calls
MAX_RETRIES = 3

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
        
        # Call Gemini API
        response = model.generate_content(full_prompt)
        
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
        
        return result
    
    except Exception as e:
        import traceback
        logger.error(f"Balance sheet generation error: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "error": f"Failed to generate balance sheet: {str(e)}",
            "generated_at": datetime.now().isoformat()
        }

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
        
        # Call Gemini API
        response = model.generate_content(full_prompt)
        
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
                "income_statement": {
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
    5. Beginning and Ending Cash Balance
    
    Also provide the following:
    1. A summary of the cash flow position
    2. Key cash flow metrics (free cash flow, cash conversion cycle, etc.)
    3. Insights and recommendations based on the cash flow statement
    4. Quarter-over-quarter or year-over-year comparisons if data is available
    
    Format your response as a JSON with the following structure:
    {
        "cash_flow_statement": {
            "operating_activities": {...},
            "investing_activities": {...},
            "financing_activities": {...},
            "net_change_in_cash": {...},
            "beginning_cash": {...},
            "ending_cash": {...}
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
        
        # Call Gemini API
        response = model.generate_content(full_prompt)
        
        # Extract JSON from response
        response_text = response.text
        logger.debug("Received response from Gemini AI")
        
        # Handle potential formatting issues in the response
        try:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx <= 0:
                logger.error("No valid JSON found in AI response for cash flow")
                raise json.JSONDecodeError("No JSON found in response", response_text, 0)
                
            json_str = response_text[start_idx:end_idx]
            result = json.loads(json_str)
            
            # Verify key fields exist in the response
            if "cash_flow_statement" not in result:
                logger.error(f"Missing 'cash_flow_statement' in AI response for cash flow: {json_str[:200]}...")
                result["cash_flow_statement"] = {
                    "error": "The AI did not generate a proper cash flow statement structure."
                }
            
        except json.JSONDecodeError as json_err:
            logger.error(f"JSON parse error for cash flow: {str(json_err)}")
            # Log a portion of the problematic response for debugging
            logger.error(f"Problematic response: {response_text[:500]}...")
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
        logger.error(f"Cash flow statement generation error: {str(e)}")
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
    Generate a comprehensive financial analysis based on the financial data provided.
    
    Include the following sections:
    1. Executive Summary
    2. Quarterly Financial Performance Analysis
       - Revenue trends (with quarter-over-quarter and year-over-year comparisons)
       - Expense analysis
       - Profitability metrics
    3. Financial Health Assessment
       - Liquidity analysis
       - Solvency analysis
       - Efficiency ratios
    4. Key Performance Indicators (KPIs)
    5. Risk Assessment
    6. Strategic Recommendations
    7. Future Outlook
    
    MOST IMPORTANT: Your response MUST include these EXACT JSON structures for chart visualization:
    
    1. "quarterly_performance": An object with quarters as keys (like "Q1 2023", "Q2 2023") derived from the actual data periods,
       and each value containing revenue, expenses, profit, and margin for that quarter.
       Example:
       "quarterly_performance": {
         "Q1 2023": {"revenue": 120000, "expenses": 95000, "profit": 25000, "margin": 20.83},
         "Q2 2023": {"revenue": 135000, "expenses": 105000, "profit": 30000, "margin": 22.22}
       }
    
    2. "expense_breakdown": An object with expense categories extracted from the actual data as keys 
       and arrays of quarterly values that match the quarters in quarterly_performance.
       Example:
       "expense_breakdown": {
         "Marketing": [25000, 28000, 30000, 35000],
         "Operations": [45000, 47000, 50000, 55000]
       }
    
    3. "financial_ratios": An object with ratio names as keys and arrays of quarterly values.
       Example:
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
        
        # Call Gemini API
        response = model.generate_content(full_prompt)
        
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
                "analysis": {
                    "error": "Failed to parse AI response. Please try again."
                },
                "raw_response": response_text[:500]  # Truncate for safety
            }
        
        # Add generation metadata
        result["generated_at"] = datetime.now().isoformat()
        result["source_format"] = file_data.get('format')
        
        # Ensure chart data is available, inform user if missing
        if "quarterly_performance" not in result:
            logger.error("AI model did not generate quarterly_performance data structure")
            result["error_details"] = result.get("error_details", []) + ["AI model failed to extract quarterly performance data from your file. Please try again with more detailed financial data."]
        
        if "expense_breakdown" not in result:
            logger.error("AI model did not generate expense_breakdown data structure")
            result["error_details"] = result.get("error_details", []) + ["AI model couldn't identify expense categories in your data. Please ensure your file contains expense information."]
        
        if "financial_ratios" not in result:
            logger.error("AI model did not generate financial_ratios data structure")
            result["error_details"] = result.get("error_details", []) + ["Financial ratios could not be calculated. Please ensure your file contains sufficient balance sheet and income data."]
        
        return result
    
    except Exception as e:
        import traceback
        logger.error(f"Financial analysis generation error: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "error": f"Failed to generate financial analysis: {str(e)}",
            "error_details": [
                "We couldn't process your financial data.",
                "Please ensure your file includes complete quarterly data with revenue and expense information.",
                "Try uploading a different financial data file with more detailed information."
            ],
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
    You are a financial analyst AI assistant. Answer the following financial question 
    based on the available financial data. Provide detailed, accurate information with
    relevant calculations, insights, and recommendations when appropriate.
    
    Financial Question: {user_query}
    
    Available Financial Data:
    """
    
    try:
        # Add file data to the prompt with safer handling
        data_str = ""
        
        if file_data:
            logger.debug(f"Processing {len(file_data)} data files for chat query")
            for item in file_data:
                try:
                    filename = item.get('filename', 'Unnamed file')
                    report_type = item.get('report_type', 'Unknown report')
                    
                    # Clean up data for safe serialization
                    item_data = item.get('data', {})
                    # Limit data size and handle potential serialization issues
                    try:
                        serialized_data = json.dumps(item_data, indent=2, default=str)[:2000]
                    except Exception as json_err:
                        logger.error(f"Error serializing chat data: {str(json_err)}")
                        serialized_data = str(item_data)[:2000]
                    
                    data_str += f"\nFile: {filename}\n"
                    data_str += f"Report Type: {report_type}\n"
                    data_str += f"Data: {serialized_data}...\n"
                except Exception as item_err:
                    logger.error(f"Error processing data item: {str(item_err)}")
                    continue
        
        if not data_str:
            data_str = "No financial data available. Please upload financial data files first."
        
        logger.debug("Preparing prompt for chat query")
        full_prompt = prompt + data_str
        
        # Call Gemini API
        response = model.generate_content(full_prompt)
        logger.debug("Received chat response from Gemini AI")
        
        return response.text
    
    except Exception as e:
        import traceback
        logger.error(f"Chat query error: {str(e)}")
        logger.error(traceback.format_exc())
        return f"Error processing your question: {str(e)}. Please try again with a more specific question or upload different financial data."

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
    
    try:
        # Sanitize report type for the prompt
        safe_report_type = str(report_type).replace('\n', ' ').replace('\r', ' ')
        
        # Prepare report data for the prompt, handling potential issues
        try:
            report_data_str = json.dumps(report_data, indent=2, default=str)
        except Exception as json_err:
            logger.error(f"Error serializing report data: {str(json_err)}")
            # Fallback to safer conversion
            report_data_str = str(report_data)
        
        prompt = f"""
        Explain the methodology and reasoning behind the financial insights and recommendations 
        provided in the {safe_report_type} report. Include:
        
        1. What financial principles or accounting standards were applied
        2. Key data points that influenced the conclusions
        3. The analytical process used to derive insights
        4. How the recommendations were prioritized
        5. Any limitations in the analysis due to data constraints
        
        Format your response in a clear, structured manner with proper headings and sections.
        Use markdown formatting for headings (# for main headings, ## for subheadings).
        Use bullet points where appropriate to improve readability.
        
        Your explanation should be easy to understand but technically precise,
        suitable for financial professionals who need to understand the AI's decision-making process.
        
        Report Data:
        {report_data_str}
        """
        
        logger.debug(f"Generating explainability for {safe_report_type} report")
        response = model.generate_content(prompt)
        
        explanation = {
            "explanation": response.text,
            "report_type": safe_report_type,
            "generated_at": datetime.now().isoformat()
        }
        
        return explanation
    
    except Exception as e:
        import traceback
        logger.error(f"Explainability generation error: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "error": f"Failed to generate explanation: {str(e)}",
            "report_type": str(report_type),
            "generated_at": datetime.now().isoformat()
        }
