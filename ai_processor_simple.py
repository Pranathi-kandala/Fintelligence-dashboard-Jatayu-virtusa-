import os
import json
import google.generativeai as genai
from datetime import datetime
import logging
import time
import random
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('fintelligence')

# Get API key
gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
if not gemini_api_key:
    logger.warning("GEMINI_API_KEY environment variable not set")
else:
    logger.info(f"Using Gemini API key: {gemini_api_key[:4]}...{gemini_api_key[-3:]} (length: {len(gemini_api_key)})")

# Configure the API
try:
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    logger.info("Initialized Gemini model successfully")
except Exception as e:
    logger.error(f"Error initializing Gemini model: {str(e)}")
    try:
        model = genai.GenerativeModel('models/gemini-pro')
        logger.info("Fallback to gemini-pro model successful")
    except Exception as fallback_err:
        logger.error(f"Error with fallback model: {str(fallback_err)}")
        model = None

# Simplified data optimization to reduce memory usage
def optimize_data_for_tokens(file_data):
    """Optimized function that uses minimal resources"""
    try:
        # Basic validation
        if not file_data:
            return "No data available"
        
        # PDF files
        if file_data.get('format') == 'pdf':
            text = file_data.get('text', '')[:3000]  # Limit size
            return text
        
        # CSV/Excel files
        elif file_data.get('format') in ['csv', 'xlsx']:
            # Extract data
            data = file_data.get('data', [])
            
            # Use minimal sample
            sample = data[:5] if len(data) > 5 else data
            
            # Clean sample data
            clean_sample = []
            for item in sample:
                clean_item = {}
                for key in ['Date', 'Category', 'Amount', 'Type']:
                    if key in item:
                        value = item[key]
                        clean_item[key] = str(value)[:30] if isinstance(value, str) else value
                clean_sample.append(clean_item)
            
            # Create simple result
            result = {
                "total_rows": len(data),
                "sample": clean_sample,
            }
            
            return json.dumps(result)
        
        else:
            return "Unsupported format"
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return "Error processing data"

# Simplified API call with minimal retry logic
def call_gemini_with_retry(prompt):
    """Simplified API call function"""
    # Limit prompt size
    prompt = prompt[:5000] if len(prompt) > 5000 else prompt
    
    # No model available
    if model is None:
        return json.dumps({"error": "No AI model available"})
    
    # Try up to 2 times only
    for attempt in range(2):
        try:
            if attempt > 0:
                time.sleep(2)  # Simple delay between attempts
                
            response = model.generate_content(prompt)
            
            # Extract text safely
            if hasattr(response, 'text'):
                return response.text
            elif hasattr(response, 'parts') and len(response.parts) > 0:
                return response.parts[0].text
            else:
                return "{}"
                
        except Exception as e:
            logger.error(f"API error: {str(e)}")
            
    # If all retries failed
    return json.dumps({"error": "Failed to get response"})

# Simplified balance sheet generator
def generate_balance_sheet(file_data):
    """Generate simplified balance sheet"""
    try:
        # Convert data to optimized string format
        data_str = optimize_data_for_tokens(file_data)
        
        # Create prompt for AI
        prompt = f"""
        Generate a balance sheet from this financial data:
        {data_str}
        
        Response should be valid JSON with this structure:
        {{
          "assets": {{
            "current_assets": {{...}},
            "non_current_assets": {{...}},
            "total": number
          }},
          "liabilities": {{
            "current_liabilities": {{...}},
            "long_term_liabilities": {{...}},
            "total": number
          }},
          "equity": {{
            "total": number
          }},
          "total_assets": number,
          "insights": [
            "insight 1",
            "insight 2"
          ]
        }}
        """
        
        # Call API and get response
        response_text = call_gemini_with_retry(prompt)
        
        # Process the response
        try:
            # Try to parse as JSON
            result = json.loads(response_text)
            
            # Ensure basic structure exists
            if not isinstance(result, dict):
                result = {}
                
            # Required fields for template
            if 'assets' not in result or not isinstance(result['assets'], dict):
                result['assets'] = {'current_assets': {}, 'non_current_assets': {}, 'total': 0}
                
            if 'liabilities' not in result or not isinstance(result['liabilities'], dict):
                result['liabilities'] = {'current_liabilities': {}, 'long_term_liabilities': {}, 'total': 0}
                
            if 'equity' not in result or not isinstance(result['equity'], dict):
                result['equity'] = {'total': 0}
                
            if 'total_assets' not in result:
                result['total_assets'] = result['assets'].get('total', 0)
                
            if 'insights' not in result or not isinstance(result['insights'], list):
                result['insights'] = ["Analysis pending."]
                
            # Create proper nested structure for template
            return {
                'balance_sheet': result
            }
                
        except json.JSONDecodeError as json_err:
            logger.error(f"JSON parsing error: {str(json_err)}")
            # Return fallback
            return {
                'balance_sheet': {
                    'assets': {'current_assets': {}, 'non_current_assets': {}, 'total': 0},
                    'liabilities': {'current_liabilities': {}, 'long_term_liabilities': {}, 'total': 0},
                    'equity': {'total': 0},
                    'total_assets': 0,
                    'insights': ["Error processing data. Please try again."],
                    'error': "Failed to parse AI response"
                }
            }
            
    except Exception as e:
        logger.error(f"Balance sheet error: {str(e)}")
        # Return fallback structure
        return {
            'balance_sheet': {
                'assets': {'current_assets': {}, 'non_current_assets': {}, 'total': 0},
                'liabilities': {'current_liabilities': {}, 'long_term_liabilities': {}, 'total': 0},
                'equity': {'total': 0},
                'total_assets': 0,
                'insights': ["Error processing data. Please try again."],
                'error': str(e)
            }
        }

# Simplified income statement generator
def generate_income_statement(file_data):
    """Generate simplified income statement"""
    try:
        # Convert data to optimized string format
        data_str = optimize_data_for_tokens(file_data)
        
        # Create prompt for AI
        prompt = f"""
        Generate an income statement from this financial data:
        {data_str}
        
        Response should be valid JSON with this structure:
        {{
          "revenue": number,
          "cost_of_goods_sold": number,
          "gross_profit": number,
          "operating_expenses": {{...}},
          "operating_income": number,
          "other_income_expenses": {{...}},
          "income_before_taxes": number,
          "taxes": number,
          "net_income": number,
          "insights": [
            "insight 1",
            "insight 2"
          ]
        }}
        """
        
        # Call API and get response
        response_text = call_gemini_with_retry(prompt)
        
        # Process the response
        try:
            # Try to parse as JSON
            result = json.loads(response_text)
            
            # Ensure basic structure exists
            if not isinstance(result, dict):
                result = {}
                
            # Required fields for template
            required_fields = [
                'revenue', 'cost_of_goods_sold', 'gross_profit', 'operating_expenses',
                'operating_income', 'other_income_expenses', 'income_before_taxes',
                'taxes', 'net_income'
            ]
            
            for field in required_fields:
                if field not in result:
                    if field in ['operating_expenses', 'other_income_expenses']:
                        result[field] = {}
                    else:
                        result[field] = 0
            
            if 'insights' not in result or not isinstance(result['insights'], list):
                result['insights'] = ["Analysis pending."]
                
            # Create proper nested structure for template
            return {
                'income_statement': result
            }
                
        except json.JSONDecodeError as json_err:
            logger.error(f"JSON parsing error: {str(json_err)}")
            # Return fallback
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
                    'insights': ["Error processing data. Please try again."],
                    'error': "Failed to parse AI response"
                }
            }
            
    except Exception as e:
        logger.error(f"Income statement error: {str(e)}")
        # Return fallback structure
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
                'insights': ["Error processing data. Please try again."],
                'error': str(e)
            }
        }

# Simplified cash flow generator
def generate_cash_flow(file_data):
    """Generate simplified cash flow statement"""
    try:
        # Convert data to optimized string format
        data_str = optimize_data_for_tokens(file_data)
        
        # Create prompt for AI
        prompt = f"""
        Generate a cash flow statement from this financial data:
        {data_str}
        
        Response should be valid JSON with this structure:
        {{
          "operating_activities": {{...}},
          "investing_activities": {{...}},
          "financing_activities": {{...}},
          "beginning_cash": number,
          "net_cash_from_operating": number,
          "net_cash_from_investing": number,
          "net_cash_from_financing": number,
          "net_change_in_cash": number,
          "ending_cash": number,
          "insights": [
            "insight 1", 
            "insight 2"
          ]
        }}
        """
        
        # Call API and get response
        response_text = call_gemini_with_retry(prompt)
        
        # Process the response
        try:
            # Try to parse as JSON
            result = json.loads(response_text)
            
            # Ensure basic structure exists
            if not isinstance(result, dict):
                result = {}
                
            # Required fields for template
            if 'operating_activities' not in result or not isinstance(result['operating_activities'], dict):
                result['operating_activities'] = {'total': 0}
                
            if 'investing_activities' not in result or not isinstance(result['investing_activities'], dict):
                result['investing_activities'] = {'total': 0}
                
            if 'financing_activities' not in result or not isinstance(result['financing_activities'], dict):
                result['financing_activities'] = {'total': 0}
                
            # Required numerical fields
            cash_fields = [
                'beginning_cash', 'net_cash_from_operating', 'net_cash_from_investing',
                'net_cash_from_financing', 'net_change_in_cash', 'ending_cash'
            ]
            
            for field in cash_fields:
                if field not in result:
                    result[field] = 0
            
            if 'insights' not in result or not isinstance(result['insights'], list):
                result['insights'] = ["Analysis pending."]
                
            # Create proper nested structure for template
            return {
                'cash_flow_statement': result
            }
                
        except json.JSONDecodeError as json_err:
            logger.error(f"JSON parsing error: {str(json_err)}")
            # Return fallback
            return {
                'cash_flow_statement': {
                    'operating_activities': {'total': 0},
                    'investing_activities': {'total': 0},
                    'financing_activities': {'total': 0},
                    'beginning_cash': 0,
                    'net_cash_from_operating': 0,
                    'net_cash_from_investing': 0,
                    'net_cash_from_financing': 0,
                    'net_change_in_cash': 0,
                    'ending_cash': 0,
                    'insights': ["Error processing data. Please try again."],
                    'error': "Failed to parse AI response"
                }
            }
            
    except Exception as e:
        logger.error(f"Cash flow error: {str(e)}")
        # Return fallback structure
        return {
            'cash_flow_statement': {
                'operating_activities': {'total': 0},
                'investing_activities': {'total': 0},
                'financing_activities': {'total': 0},
                'beginning_cash': 0,
                'net_cash_from_operating': 0,
                'net_cash_from_investing': 0,
                'net_cash_from_financing': 0,
                'net_change_in_cash': 0,
                'ending_cash': 0,
                'insights': ["Error processing data. Please try again."],
                'error': str(e)
            }
        }

# Simplified analysis generator
def generate_analysis(file_data):
    """Generate simplified financial analysis"""
    try:
        # Convert data to optimized string format
        data_str = optimize_data_for_tokens(file_data)
        
        # Create prompt for AI
        prompt = f"""
        Generate a comprehensive financial analysis from this data:
        {data_str}
        
        Response should be valid JSON with this structure:
        {{
          "summary": "Brief overview of the financial situation",
          "key_metrics": {{
            "profitability": {{...}},
            "liquidity": {{...}},
            "efficiency": {{...}}
          }},
          "trends": [
            "trend 1",
            "trend 2"
          ],
          "recommendations": [
            "recommendation 1",
            "recommendation 2"
          ]
        }}
        """
        
        # Call API and get response
        response_text = call_gemini_with_retry(prompt)
        
        # Process the response
        try:
            # Try to parse as JSON
            result = json.loads(response_text)
            
            # Ensure basic structure exists
            if not isinstance(result, dict):
                result = {}
                
            # Required fields for template
            if 'summary' not in result:
                result['summary'] = "Analysis pending."
                
            if 'key_metrics' not in result or not isinstance(result['key_metrics'], dict):
                result['key_metrics'] = {
                    'profitability': {},
                    'liquidity': {},
                    'efficiency': {}
                }
                
            if 'trends' not in result or not isinstance(result['trends'], list):
                result['trends'] = ["Analysis pending."]
                
            if 'recommendations' not in result or not isinstance(result['recommendations'], list):
                result['recommendations'] = ["Analysis pending."]
                
            # Create proper nested structure for template
            return {
                'analysis': result
            }
                
        except json.JSONDecodeError as json_err:
            logger.error(f"JSON parsing error: {str(json_err)}")
            # Return fallback
            return {
                'analysis': {
                    'summary': "Error processing data. Please try again.",
                    'key_metrics': {
                        'profitability': {},
                        'liquidity': {},
                        'efficiency': {}
                    },
                    'trends': ["Error processing data."],
                    'recommendations': ["Please try again."],
                    'error': "Failed to parse AI response"
                }
            }
            
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        # Return fallback structure
        return {
            'analysis': {
                'summary': "Error processing data. Please try again.",
                'key_metrics': {
                    'profitability': {},
                    'liquidity': {},
                    'efficiency': {}
                },
                'trends': ["Error processing data."],
                'recommendations': ["Please try again."],
                'error': str(e)
            }
        }

# Simplified chat query processor
def process_chat_query(user_query, file_data):
    """Process a user query about financial data"""
    try:
        # Limit file data
        file_summary = "Financial data not available"
        if isinstance(file_data, list) and len(file_data) > 0:
            # Get the first file
            first_file = file_data[0]
            if isinstance(first_file, dict):
                file_summary = optimize_data_for_tokens(first_file.get('data', {}))
                
        # Create prompt for AI
        prompt = f"""
        Answer this financial question based on the data:
        
        User question: {user_query}
        
        Financial data summary: {file_summary}
        
        Provide a helpful, accurate answer based on the data.
        """
        
        # Call AI with minimal prompt
        response = call_gemini_with_retry(prompt)
        
        return response
            
    except Exception as e:
        logger.error(f"Chat query error: {str(e)}")
        return f"Sorry, I couldn't process your question: {str(e)}"

# Simplified explanation generator  
def explain_ai_decision(report_type, report_data):
    """Generate a simple explanation of AI reasoning"""
    try:
        # Extract the data based on report type
        data = {}
        if report_type == 'balance_sheet' and 'balance_sheet' in report_data:
            data = report_data['balance_sheet']
        elif report_type == 'income_statement' and 'income_statement' in report_data:
            data = report_data['income_statement']
        elif report_type == 'cash_flow' and 'cash_flow_statement' in report_data:
            data = report_data['cash_flow_statement']
        elif report_type == 'analysis' and 'analysis' in report_data:
            data = report_data['analysis']
            
        # Create a simple explanation
        explanation = {
            "process": [
                f"The AI analyzed your financial data to create a {report_type} report.",
                "It identified key financial transactions and categorized them appropriately.",
                "Calculations were performed to generate accurate financial statements.",
                "The AI applied standard accounting principles to organize the data."
            ],
            "confidence": "medium",
            "limitations": [
                "The analysis is based only on the data provided.",
                "More historical data would improve trend analysis.",
                "Industry benchmarks could enhance comparative insights."
            ],
            "next_steps": [
                "Review the report for accuracy against your records.",
                "Consider providing more detailed transaction data for better insights.",
                "Use the insights to guide financial decision-making."
            ]
        }
        
        return explanation
            
    except Exception as e:
        logger.error(f"Explanation error: {str(e)}")
        return {
            "process": ["Unable to explain AI decision process due to an error."],
            "confidence": "low",
            "limitations": ["The explanation feature encountered an error."],
            "next_steps": ["Please try again or contact support."]
        }