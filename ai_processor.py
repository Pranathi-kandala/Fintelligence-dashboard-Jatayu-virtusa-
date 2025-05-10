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
                
                # Add category breakdown if available
                categories = financial_data.get('by_category', {})
                expense_categories = {k: v for k, v in categories.items() if v.get('expenses', 0) > 0}
                
                if expense_categories:
                    top_categories = sorted(expense_categories.items(), key=lambda x: x[1].get('expenses', 0), reverse=True)[:3]
                    response += "Your top expense categories are "
                    response += ", ".join([f"{cat} (${data.get('expenses', 0):,.2f})" for cat, data in top_categories])
                    response += "."
            
            # Profit questions
            elif any(term in question_lower for term in ['profit', 'margin', 'profitability']):
                profit_margin = (net_income / income) * 100 if income > 0 else 0
                response = f"Your net income is ${net_income:,.2f} with a profit margin of {profit_margin:.1f}%. "
                
                if profit_margin > 20:
                    response += "This is a strong profit margin compared to industry averages."
                elif profit_margin > 10:
                    response += "This is a good profit margin within normal industry ranges."
                elif profit_margin > 0:
                    response += "This is a positive but below-average profit margin."
                else:
                    response += "You are currently operating at a loss."
            
            # Time series questions
            elif any(term in question_lower for term in ['trend', 'growth', 'over time', 'monthly', 'quarterly']):
                months = financial_data.get('by_month', {})
                quarters = financial_data.get('quarters', {})
                
                if months:
                    sorted_months = sorted(months.keys())
                    if len(sorted_months) > 1:
                        first_month = months[sorted_months[0]]
                        last_month = months[sorted_months[-1]]
                        
                        first_income = first_month.get('income', 0)
                        last_income = last_month.get('income', 0)
                        
                        if first_income > 0:
                            growth_rate = ((last_income - first_income) / first_income) * 100
                            response = f"Your revenue growth from {sorted_months[0]} to {sorted_months[-1]} was {growth_rate:.1f}%. "
                        
                        response += f"Your most recent monthly revenue was ${last_income:,.2f}."
                
                elif quarters:
                    response = "Quarterly financial data is available. "
                    sorted_quarters = sorted(quarters.keys())
                    
                    if len(sorted_quarters) > 1:
                        quarters_income = [quarters[q].get('income', 0) for q in sorted_quarters]
                        
                        response += f"Revenue for {sorted_quarters[-1]} was ${quarters_income[-1]:,.2f}, "
                        
                        if quarters_income[-1] > quarters_income[-2]:
                            increase = ((quarters_income[-1] - quarters_income[-2]) / quarters_income[-2]) * 100
                            response += f"up {increase:.1f}% from the previous quarter."
                        else:
                            decrease = ((quarters_income[-2] - quarters_income[-1]) / quarters_income[-2]) * 100
                            response += f"down {decrease:.1f}% from the previous quarter."
            
            # Account questions
            elif any(term in question_lower for term in ['account', 'accounts', 'cash']):
                accounts = financial_data.get('by_account', {})
                
                if accounts:
                    # List top accounts by net value
                    top_accounts = sorted(accounts.items(), key=lambda x: abs(x[1].get('net', 0)), reverse=True)[:3]
                    
                    response = "Your top account balances are: "
                    response += ", ".join([f"{acct}: ${data.get('net', 0):,.2f}" for acct, data in top_accounts])
                    response += "."
                else:
                    response = "Account-specific information is not available in your financial data."
            
            # Default response for other questions
            else:
                response = f"Based on your financial data, your total revenue is ${income:,.2f} and total expenses are ${expenses:,.2f}, resulting in a net income of ${net_income:,.2f}."
                
                if income > 0:
                    profit_margin = (net_income / income) * 100
                    response += f" Your profit margin is {profit_margin:.1f}%."
        else:
            # Check if it's a general finance question that can be answered without specific data
            query_lower = user_query.lower()
            
            # Provide general explanations for common financial terms
            if "what is" in query_lower or "explain" in query_lower or "define" in query_lower or "how does" in query_lower:
                
                # Cashflow related questions
                if "cash flow" in query_lower or "cashflow" in query_lower:
                    return "Cash flow refers to the net amount of cash moving in and out of a business during a specific period. Positive cash flow indicates more money coming in than going out, while negative cash flow means more money is leaving than coming in. Cash flow is divided into three categories: operating (from core business activities), investing (from assets and investments), and financing (from debt and equity financing). Healthy cash flow is essential for business sustainability and growth, regardless of profitability."
                
                # Balance sheet related questions
                elif "balance sheet" in query_lower:
                    return "A balance sheet is a financial statement that reports a company's assets, liabilities, and equity at a specific point in time. It provides a snapshot of what a company owns (assets), what it owes (liabilities), and the value that's left for shareholders (equity). The fundamental accounting equation that governs a balance sheet is: Assets = Liabilities + Equity. Balance sheets help assess a company's financial position, liquidity, and solvency."
                
                # Income statement related questions
                elif "income statement" in query_lower or "profit and loss" in query_lower or "p&l" in query_lower:
                    return "An income statement, also known as a profit and loss statement (P&L), shows a company's revenues, expenses, and profits over a specific period. Unlike the balance sheet, which presents a snapshot at a point in time, the income statement covers a range of time (quarter, year). It follows a simple formula: Revenue - Expenses = Profit/Loss. Income statements help evaluate a company's profitability, operational efficiency, and performance trends."
                
                # Revenue related questions
                elif "revenue" in query_lower or "sales" in query_lower or "income" in query_lower:
                    return "Revenue, or sales, represents the total amount of money generated from selling products or services before any expenses are deducted. It's the top line of an income statement and a fundamental indicator of a company's market success. Revenue growth often signals business expansion, increased market share, or improved pricing strategies, though it doesn't necessarily indicate profitability without considering associated costs."
                
                # Expense related questions
                elif "expense" in query_lower or "cost" in query_lower or "expenditure" in query_lower:
                    return "Expenses are the costs incurred by a business to generate revenue. They include operating expenses (like rent, salaries, utilities), cost of goods sold (direct costs of products), and non-operating expenses (like interest payments). Understanding and managing expenses is crucial for profitability. Expenses are categorized as fixed (constant regardless of business activity) or variable (changing with business volume), and proper expense management directly impacts bottom-line profit."
                
                # Profit related questions
                elif "profit" in query_lower or "margin" in query_lower or "net income" in query_lower:
                    return "Profit represents the financial gain when revenue exceeds expenses. There are several types of profit on an income statement: Gross profit (Revenue - Cost of goods sold), Operating profit (Gross profit - Operating expenses), and Net profit (Operating profit - Taxes and interest). Profit margins express profit as a percentage of revenue, allowing comparison across different sized companies or time periods. Improving profit requires either increasing revenue, decreasing costs, or both."
                
                # Asset related questions
                elif "asset" in query_lower:
                    return "Assets are resources owned by a company that have economic value and are expected to provide future benefits. They appear on the balance sheet and are categorized as current assets (convertible to cash within a year, like inventory) or non-current assets (long-term, like property and equipment). Assets can be tangible (physical) or intangible (non-physical, like patents). The management of assets directly impacts a company's operational efficiency, liquidity, and overall financial health."
                
                # Liability related questions
                elif "liability" in query_lower or "debt" in query_lower:
                    return "Liabilities are financial obligations or debts a company owes to others. They appear on the balance sheet and represent claims against the company's assets. Liabilities are categorized as current (due within a year, like accounts payable) or non-current (long-term, like mortgages). They play a crucial role in assessing a company's financial risk, solvency, and leverage. While debt can provide capital for growth, excessive liabilities may lead to financial distress."
                
                # ROI related questions
                elif "roi" in query_lower or "return on investment" in query_lower:
                    return "Return on Investment (ROI) measures the profitability of an investment relative to its cost. It's calculated as: ROI = (Net Profit / Cost of Investment) × 100%. A positive ROI indicates a profitable investment, while a negative ROI shows a loss. ROI helps evaluate investment efficiency and compare different investment opportunities. However, it doesn't account for time value of money or risk factors, which are considered in more comprehensive metrics like IRR or NPV."
            
            # Default response if no specific pattern is matched
            response = "I couldn't find specific information in your financial data to answer this question accurately. For personalized insights, please try asking about your revenue, expenses, profits, or specific accounts in your data."
        
        return response
    
    except Exception as e:
        logger.error(f"Error processing chat query: {str(e)}")
        return f"I'm sorry, I encountered an error while analyzing your financial data: {str(e)}. Please try again with a different question or upload a different financial dataset."

def explain_ai_decision(report_type, report_data):
    """
    Generate an explanation of how the AI reached its conclusions for a report
    
    Args:
        report_type (str): Type of report (balance_sheet, income_statement, cash_flow, analysis)
        report_data (dict): Report data generated by the AI
        
    Returns:
        dict: Explanation of AI decision process
    """
    try:
        # Create an explanation based on the report type and data
        explanation = {
            "process": [],
            "confidence": "medium",
            "limitations": [],
            "next_steps": []
        }
        
        # General process steps for all report types
        explanation["process"].append("Extracted financial transaction data from your uploaded file.")
        explanation["process"].append("Identified transaction types, accounts, categories, and dates.")
        
        # Report-specific process steps
        if report_type == 'balance_sheet':
            explanation["process"].append("Classified accounts as assets or liabilities based on transaction patterns.")
            explanation["process"].append("Calculated current and non-current asset values from account balances.")
            explanation["process"].append("Identified liability obligations and categorized as short or long-term.")
            explanation["process"].append("Calculated equity as the difference between assets and liabilities.")
            
            # Confidence based on data quality
            data = report_data.get('balance_sheet', {})
            assets = data.get('assets', {}).get('total', 0)
            
            if assets > 0:
                explanation["confidence"] = "high"
            
            # Limitations
            explanation["limitations"].append("Asset and liability classification was based on account names and transaction patterns.")
            explanation["limitations"].append("Long-term assets and depreciation were estimated from available data.")
            
            # Next steps
            explanation["next_steps"].append("Verify asset and liability classifications for accuracy.")
            explanation["next_steps"].append("Review equity calculations and ensure all accounts are properly categorized.")
            
        elif report_type == 'income_statement':
            explanation["process"].append("Identified revenue and expense transactions from financial data.")
            explanation["process"].append("Calculated gross profit by separating cost of goods sold from other expenses.")
            explanation["process"].append("Categorized operating and non-operating expenses based on transaction types.")
            explanation["process"].append("Estimated tax implications to calculate net income after taxes.")
            
            # Confidence based on data quality
            data = report_data.get('income_statement', {})
            revenue = data.get('revenue', 0)
            
            if revenue > 0:
                explanation["confidence"] = "high"
            
            # Limitations
            explanation["limitations"].append("Cost of goods sold was estimated based on transaction categories.")
            explanation["limitations"].append("Tax calculations are estimates and may not reflect actual tax obligations.")
            
            # Next steps
            explanation["next_steps"].append("Review expense categorizations for accuracy.")
            explanation["next_steps"].append("Verify revenue recognition and expense allocation to periods.")
            
        elif report_type == 'cash_flow':
            explanation["process"].append("Separated cash flow activities into operating, investing, and financing categories.")
            explanation["process"].append("Calculated beginning and ending cash balances based on transaction data.")
            explanation["process"].append("Determined net cash flow from each activity type based on transaction patterns.")
            explanation["process"].append("Reconciled cash flow statements with income and balance sheet data.")
            
            # Confidence based on data quality
            data = report_data.get('cash_flow_statement', {})
            operating = data.get('net_cash_from_operating', 0)
            
            if operating != 0:
                explanation["confidence"] = "high"
            
            # Limitations
            explanation["limitations"].append("Cash flow categorization was based on transaction descriptions and categories.")
            explanation["limitations"].append("Non-cash transactions may not be fully reflected in the cash flow statement.")
            
            # Next steps
            explanation["next_steps"].append("Verify cash flow activity classifications.")
            explanation["next_steps"].append("Reconcile cash flow data with bank statements and other financial records.")
            
        elif report_type == 'analysis':
            explanation["process"].append("Calculated key financial metrics including profitability, liquidity, and efficiency ratios.")
            explanation["process"].append("Analyzed financial trends over time using monthly and quarterly data.")
            explanation["process"].append("Compared performance metrics to identify strengths and improvement areas.")
            explanation["process"].append("Generated actionable recommendations based on financial health indicators.")
            
            # Confidence based on data quality
            data = report_data.get('analysis', {})
            metrics = data.get('key_metrics', {})
            
            if metrics and len(metrics) > 0:
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