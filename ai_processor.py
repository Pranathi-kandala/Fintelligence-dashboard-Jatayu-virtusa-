"""
AI Financial Processor
Processes financial data to generate actual reports using real analysis
"""

import os
import json
import logging
from datetime import datetime
import tempfile
import csv
import re
import time
import random
import google.generativeai as genai
import requests

# Import the financial data processor functions
from financial_data_processor import (
    analyze_csv_data,
    generate_balance_sheet,
    generate_income_statement,
    generate_cash_flow,
    generate_financial_analysis
)

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('fintelligence')

# Get API key
gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
if gemini_api_key:
    logger.info(f"Using Gemini API key: {gemini_api_key[:4]}...{gemini_api_key[-3:]} (length: {len(gemini_api_key)})")
    
    # Configure the Gemini API
    genai.configure(api_key=gemini_api_key)
    
    # Set up the model
    # the newest Gemini model is "gemini-1.5-pro" which was released after March 2023
    generation_config = {
        "temperature": 0.2,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
    }
    
    # Initialize the model
    try:
        gemini_model = genai.GenerativeModel(model_name="gemini-1.5-pro", 
                                            generation_config=generation_config)
        logger.info("Successfully initialized Gemini model")
    except Exception as e:
        logger.error(f"Error initializing Gemini model: {str(e)}")
        gemini_model = None
else:
    logger.warning("GEMINI_API_KEY environment variable not set")
    gemini_model = None

def call_gemini_chat(prompt, chat_history=None):
    """
    Call Gemini API for chat responses with retry logic
    
    Args:
        prompt (str): The user's question
        chat_history (list, optional): Previous chat history for context
        
    Returns:
        str: The AI response
    """
    if not gemini_api_key or not gemini_model:
        return "Sorry, the Gemini API is not configured. Please ensure the API key is set properly."
    
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # Create context with financial expertise
            financial_expert_prompt = """You are an AI-powered financial advisor assistant for Fintelligence.
            You specialize in explaining financial concepts and analyzing financial data.
            When explaining financial terms, be clear, concise, and use simple language.
            When analyzing data, focus on actionable insights and patterns.
            Be helpful, professional, and answer in simple terms that anyone can understand."""
            
            # Add any financial data context if provided
            if chat_history:
                chat = gemini_model.start_chat(history=chat_history)
                response = chat.send_message(prompt)
            else:
                # For the first message, include the expert prompt
                messages = [financial_expert_prompt, prompt]
                response = gemini_model.generate_content(messages)
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error calling Gemini API (attempt {attempt+1}/{max_retries}): {str(e)}")
            if "rate limit" in str(e).lower():
                logger.warning(f"Rate limit hit, retrying in {retry_delay} seconds")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                # For other errors, return a fallback response
                return f"I encountered an error while processing your question. Please try again or ask something different. Technical details: {str(e)}"
    
    return "I'm sorry, but I'm experiencing high traffic at the moment. Please try asking your question again in a moment."

def optimize_data_for_tokens(file_data):
    """
    Extract and process CSV data for financial analysis
    
    Args:
        file_data (dict): Raw financial data from file processor
        
    Returns:
        object: Processed financial data for reports
    """
    try:
        # For PDF files, just return text
        if file_data.get('format') == 'pdf':
            text = file_data.get('text', '')
            logger.debug(f"Extracted {len(text)} characters from PDF")
            return text
        
        # For CSV/Excel files, use the financial data processor
        elif file_data.get('format') in ['csv', 'xlsx']:
            logger.debug(f"Processing {file_data.get('format')} file with {len(file_data.get('data', []))} rows")
            
            # Create a temporary CSV file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
                temp_path = temp_file.name
                
                # Get the data and columns
                data = file_data.get('data', [])
                columns = file_data.get('columns', [])
                
                # Write data to temporary CSV
                writer = csv.DictWriter(temp_file, fieldnames=columns)
                writer.writeheader()
                writer.writerows(data)
            
            # Process the CSV file
            try:
                financial_data = analyze_csv_data(temp_path)
                os.unlink(temp_path)  # Clean up temporary file
                return financial_data
            except Exception as e:
                logger.error(f"Error analyzing CSV data: {str(e)}")
                os.unlink(temp_path)  # Make sure to clean up on error
                raise
        
        # Unsupported format
        else:
            logger.warning(f"Unsupported file format: {file_data.get('format')}")
            return "Unsupported file format"
    
    except Exception as e:
        logger.error(f"Error in optimize_data_for_tokens: {str(e)}")
        return f"Error processing data: {str(e)}"

def call_gemini_with_retry(prompt):
    """
    Log API call details but use local processing instead of external API
    
    Args:
        prompt (str): The prompt text to send to the API (used for logging only)
        
    Returns:
        str: Empty response - actual processing done in generator functions
    """
    # Just log the call but don't actually call the API
    logger.info(f"Would call API with prompt length: {len(prompt)}")
    logger.info(f"API key status: {'Valid' if len(gemini_api_key) > 20 else 'Missing or Invalid'}")
    
    # Return empty response - actual processing done in generator functions
    return "{}"

def generate_balance_sheet(file_data):
    """
    Generate a balance sheet from real financial data
    
    Args:
        file_data (dict): Processed financial data
        
    Returns:
        dict: Balance sheet data and insights
    """
    try:
        logger.debug(f"Generating balance_sheet report for file ID: {file_data.get('id', 'unknown')}")
        logger.debug(f"File data format: {file_data.get('format', 'unknown')}")
        logger.debug(f"File data columns: {file_data.get('columns', [])}")
        
        # Process the financial data
        financial_data = optimize_data_for_tokens(file_data)
        
        # Check if we got a string error message instead of financial data
        if isinstance(financial_data, str):
            logger.error(f"Failed to process file data: {financial_data}")
            raise ValueError(f"Failed to process file data: {financial_data}")
        
        # Call the financial data processor to generate the report
        from financial_data_processor import generate_balance_sheet as generate_bs
        return generate_bs(financial_data)
    
    except Exception as e:
        logger.error(f"Error generating balance sheet: {str(e)}")
        return {
            'balance_sheet': {
                'assets': {'current_assets': {}, 'non_current_assets': {}, 'total': 0},
                'liabilities': {'current_liabilities': {}, 'long_term_liabilities': {}, 'total': 0},
                'equity': {'total': 0},
                'total_assets': 0,
                'insights': [f"Error generating balance sheet: {str(e)}"],
                'error': str(e)
            }
        }

def generate_income_statement(file_data):
    """
    Generate an income statement from real financial data
    
    Args:
        file_data (dict): Processed financial data
        
    Returns:
        dict: Income statement data and insights
    """
    try:
        logger.debug(f"Generating income_statement report for file ID: {file_data.get('id', 'unknown')}")
        logger.debug(f"File data format: {file_data.get('format', 'unknown')}")
        logger.debug(f"File data columns: {file_data.get('columns', [])}")
        
        # Process the financial data
        financial_data = optimize_data_for_tokens(file_data)
        
        # Check if we got a string error message instead of financial data
        if isinstance(financial_data, str):
            logger.error(f"Failed to process file data: {financial_data}")
            raise ValueError(f"Failed to process file data: {financial_data}")
        
        # Call the financial data processor to generate the report
        from financial_data_processor import generate_income_statement as generate_is
        return generate_is(financial_data)
    
    except Exception as e:
        logger.error(f"Error generating income statement: {str(e)}")
        return {
            'income_statement': {
                'revenue': 0,
                'cost_of_goods_sold': 0,
                'gross_profit': 0,
                'operating_expenses': {},
                'operating_income': 0,
                'other_income_expenses': {},
                'income_before_taxes': 0,
                'taxes': 0,
                'net_income': 0,
                'insights': [f"Error generating income statement: {str(e)}"],
                'error': str(e)
            }
        }

def generate_cash_flow(file_data):
    """
    Generate a cash flow statement from real financial data
    
    Args:
        file_data (dict): Processed financial data
        
    Returns:
        dict: Cash flow statement data and insights
    """
    try:
        logger.debug(f"Generating cash_flow report for file ID: {file_data.get('id', 'unknown')}")
        logger.debug(f"File data format: {file_data.get('format', 'unknown')}")
        logger.debug(f"File data columns: {file_data.get('columns', [])}")
        
        # Process the financial data
        financial_data = optimize_data_for_tokens(file_data)
        
        # Check if we got a string error message instead of financial data
        if isinstance(financial_data, str):
            logger.error(f"Failed to process file data: {financial_data}")
            raise ValueError(f"Failed to process file data: {financial_data}")
        
        # Call the financial data processor to generate the report
        from financial_data_processor import generate_cash_flow as generate_cf
        return generate_cf(financial_data)
    
    except Exception as e:
        logger.error(f"Error generating cash flow statement: {str(e)}")
        return {
            'cash_flow_statement': {
                'operating_activities': {},
                'investing_activities': {},
                'financing_activities': {},
                'beginning_cash': 0,
                'net_cash_from_operating': 0,
                'net_cash_from_investing': 0,
                'net_cash_from_financing': 0,
                'net_change_in_cash': 0,
                'ending_cash': 0,
                'insights': [f"Error generating cash flow statement: {str(e)}"],
                'error': str(e)
            }
        }

def generate_analysis(file_data):
    """
    Generate a comprehensive financial analysis from real financial data
    
    Args:
        file_data (dict): Processed financial data
        
    Returns:
        dict: Financial analysis data and insights
    """
    try:
        logger.debug(f"Generating analysis report for file ID: {file_data.get('id', 'unknown')}")
        logger.debug(f"File data format: {file_data.get('format', 'unknown')}")
        logger.debug(f"File data columns: {file_data.get('columns', [])}")
        
        # Process the financial data
        financial_data = optimize_data_for_tokens(file_data)
        
        # Check if we got a string error message instead of financial data
        if isinstance(financial_data, str):
            logger.error(f"Failed to process file data: {financial_data}")
            raise ValueError(f"Failed to process file data: {financial_data}")
        
        # Call the financial data processor to generate the report
        from financial_data_processor import generate_financial_analysis
        return generate_financial_analysis(financial_data)
    
    except Exception as e:
        logger.error(f"Error generating financial analysis: {str(e)}")
        return {
            'analysis': {
                'summary': f"Error generating financial analysis: {str(e)}",
                'key_metrics': {
                    'profitability': {},
                    'liquidity': {},
                    'efficiency': {}
                },
                'trends': [f"Error generating financial analysis: {str(e)}"],
                'recommendations': ["Please try again with valid financial data."],
                'error': str(e)
            }
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
    try:
        # Basic error handling
        if not user_query:
            return "Please provide a question about your financial data."
        
        # Prepare financial context for Gemini
        financial_context = ""
        
        if file_data and isinstance(file_data, list) and len(file_data) > 0:
            # Process most recent file data
            recent_file = file_data[0]
            financial_data = optimize_data_for_tokens(recent_file.get('data', {}))
            
            if financial_data and isinstance(financial_data, dict):
                # Extract key financial metrics
                income = financial_data.get('income', 0)
                expenses = financial_data.get('expenses', 0)
                net_income = income - expenses  # Calculate in case it's not provided
                
                # Build context for Gemini
                financial_context = f"""
                Financial data context:
                - Total Revenue: ${income:,.2f}
                - Total Expenses: ${expenses:,.2f}
                - Net Income: ${net_income:,.2f}
                """
                
                # Add account information
                accounts = financial_data.get('by_account', {})
                if accounts:
                    financial_context += "- Top Account Balances:\n"
                    top_accounts = sorted(accounts.items(), key=lambda x: abs(x[1].get('net', 0) if isinstance(x[1], dict) else 0), reverse=True)[:3]
                    for acct, data in top_accounts:
                        net_value = data.get('net', 0) if isinstance(data, dict) else 0
                        financial_context += f"  * {acct}: ${net_value:,.2f}\n"
                
                # Add category information
                categories = financial_data.get('by_category', {})
                if categories:
                    top_expenses = {}
                    for cat, data in categories.items():
                        if isinstance(data, dict) and data.get('expenses', 0) > 0:
                            top_expenses[cat] = data.get('expenses', 0)
                    
                    if top_expenses:
                        financial_context += "- Top Expense Categories:\n"
                        for cat, amt in sorted(top_expenses.items(), key=lambda x: x[1], reverse=True)[:3]:
                            financial_context += f"  * {cat}: ${amt:,.2f}\n"
        
        # Create appropriate prompt for Gemini based on whether we have financial data
        if financial_context:
            prompt = f"""I'd like you to answer this financial question: "{user_query}"

Here's the relevant financial data:
{financial_context}

Please provide a helpful, accurate response based on this data. If this is asking about specifics that aren't in the data, focus on the information provided."""
        else:
            prompt = f"""I'd like you to answer this financial question: "{user_query}"

Please explain this concept clearly, even though I don't have specific financial data to share. Provide a helpful explanation using simple terms."""
        
        # Call Gemini API for the response
        response = call_gemini_chat(prompt)
        
        # If response fails, fall back to a simple response
        if not response or response.startswith("Error:"):
            if "cash flow" in user_query.lower() or "cashflow" in user_query.lower():
                return "Cash flow refers to the movement of money in and out of a business. It shows whether you have enough money to pay your bills. Positive cash flow means more money coming in than going out, which is good for business health. There are three types: operating (from core business), investing (from assets), and financing (from loans or investments)."
            elif "balance sheet" in user_query.lower():
                return "A balance sheet shows what a company owns (assets), what it owes (liabilities), and the difference (equity) at a specific point in time. It follows the formula: Assets = Liabilities + Equity. This helps understand a company's financial position."
            elif "income statement" in user_query.lower():
                return "An income statement shows your revenue, expenses, and profit/loss over a period of time. It follows the simple formula: Revenue - Expenses = Profit (or Loss). This helps track your business performance."
            else:
                return "I apologize, but I couldn't process your query through our AI system. Your question was about financial topics, and I'd be happy to try answering again or you could rephrase your question."
        
        # Return the AI's response
        return response
    
    except Exception as e:
        logger.error(f"Error processing chat query: {str(e)}")
        # Provide a helpful fallback response if there's an error
        if "what is" in user_query.lower() or "explain" in user_query.lower():
            if "cash flow" in user_query.lower() or "cashflow" in user_query.lower():
                return "Cash flow refers to the movement of money in and out of a business. It shows whether you have enough money to pay your bills. Positive cash flow means more money coming in than going out, which is good for business health."
            elif "balance sheet" in user_query.lower():
                return "A balance sheet shows what a company owns (assets), what it owes (liabilities), and the difference (equity) at a specific point in time. It follows the formula: Assets = Liabilities + Equity."
            elif "income statement" in user_query.lower():
                return "An income statement shows your revenue, expenses, and profit/loss over a period of time. It follows the simple formula: Revenue - Expenses = Profit (or Loss)."
        
        return f"I'm sorry, I encountered an error while analyzing your question. Please try again or ask something different."

def explain_ai_decision(report_type, data):
    """
    Generate a natural language explanation of how the AI generated a specific report
    
    Args:
        report_type (str): Type of report (balance_sheet, income_statement, cash_flow, analysis)
        data (dict): The report data for which explanation is requested
        
    Returns:
        dict: Explanation data with process description, confidence level, limitations, and next steps
    """
    try:
        logger.debug(f"Generating explanation for {report_type} report")
        
        # Initialize explanation structure
        explanation = {
            "process": [],
            "confidence": "medium",
            "limitations": [],
            "next_steps": []
        }
        
        # Generate explanation based on report type
        if report_type == "balance_sheet":
            # Process description for balance sheet
            explanation["process"].append("The AI analyzed your financial data to identify assets, liabilities, and equity.")
            explanation["process"].append("Assets were categorized as current (cash, accounts receivable) or non-current (property, equipment).")
            explanation["process"].append("Liabilities were categorized as short-term (accounts payable) or long-term (loans, mortgages).")
            explanation["process"].append("Equity was calculated as the difference between total assets and total liabilities.")
            
            # Check data quality to determine confidence
            if data and 'balance_sheet' in data:
                bs = data['balance_sheet']
                if bs.get('assets', {}).get('total', 0) > 0 and bs.get('liabilities', {}).get('total', 0) > 0:
                    explanation["confidence"] = "high"
            
        elif report_type == "income_statement":
            # Process description for income statement
            explanation["process"].append("The AI analyzed your financial transactions to identify revenue and expense items.")
            explanation["process"].append("Revenue was categorized by source (sales, services, other income).")
            explanation["process"].append("Expenses were categorized by type (cost of goods, operating expenses, taxes).")
            explanation["process"].append("Net income was calculated by subtracting all expenses from total revenue.")
            
            # Check data quality to determine confidence
            if data and 'income_statement' in data:
                is_data = data['income_statement']
                if is_data.get('revenue', 0) > 0 and isinstance(is_data.get('operating_expenses'), dict):
                    explanation["confidence"] = "high"
            
        elif report_type == "cash_flow":
            # Process description for cash flow
            explanation["process"].append("The AI analyzed your financial data to track cash movements across operating, investing, and financing activities.")
            explanation["process"].append("Operating cash flow was derived from core business operations.")
            explanation["process"].append("Investing cash flow was calculated from asset purchases/sales.")
            explanation["process"].append("Financing cash flow was identified from debt and equity transactions.")
            explanation["process"].append("The net change in cash was determined by combining all three categories.")
            
            # Check data quality to determine confidence
            if data and 'cash_flow_statement' in data:
                cf = data['cash_flow_statement']
                if cf.get('operating_activities') and cf.get('net_change_in_cash') is not None:
                    explanation["confidence"] = "high"
            
        elif report_type == "analysis":
            # Process description for financial analysis
            explanation["process"].append("The AI conducted a comprehensive analysis of your financial data across multiple statements.")
            explanation["process"].append("Key financial metrics were calculated for profitability, liquidity, and efficiency.")
            explanation["process"].append("Historical data was analyzed to identify trends and patterns.")
            explanation["process"].append("Insights and recommendations were generated based on identified strengths and weaknesses.")
            
            # Check data quality to determine confidence
            if data and 'analysis' in data:
                analysis = data['analysis']
                if analysis.get('key_metrics') and analysis.get('recommendations'):
                    explanation["confidence"] = "high"
            
        # Limitations
        explanation["limitations"].append("Analysis is based solely on the financial data provided.")
        explanation["limitations"].append("Industry benchmarks and economic context are not included in the analysis.")
        
        # Next steps
        explanation["next_steps"].append("Consider the recommendations in light of your specific business context.")
        explanation["next_steps"].append("Review the analysis periodically as new financial data becomes available.")
        
        return explanation
    
    except Exception as e:
        logger.error(f"Error generating explanation: {str(e)}")
        return {
            "process": ["An error occurred while generating the explanation."],
            "confidence": "low",
            "limitations": ["Explanation functionality encountered an error."],
            "next_steps": ["Please try regenerating the report."]
        }