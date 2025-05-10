"""
Financial Data Processor
This module analyzes CSV financial data to generate accurate financial reports
"""

import csv
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('fintelligence')

def analyze_csv_data(file_path):
    """
    Analyze CSV financial data to extract structured information.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        dict: Structured financial data for reports
    """
    try:
        # Read the CSV file
        with open(file_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            rows = list(reader)
            
        if not rows:
            logger.error(f"No data found in CSV file: {file_path}")
            return None
            
        # Initialize financial data structure
        financial_data = {
            'transactions': rows,
            'income': 0,
            'expenses': 0,
            'net_income': 0,
            'by_category': {},
            'by_account': {},
            'by_month': {},
            'quarters': {}
        }
        
        # Process each transaction
        for row in rows:
            try:
                # Extract key fields
                amount = float(row.get('Amount', 0))
                transaction_type = row.get('Type', '')
                category = row.get('Category', 'Uncategorized')
                account = row.get('Account', 'Unknown')
                date_str = row.get('Date', '')
                
                # Track income vs expenses
                if transaction_type.lower() == 'income':
                    financial_data['income'] += amount
                elif transaction_type.lower() == 'expense':
                    financial_data['expenses'] += amount
                
                # Track by category
                if category not in financial_data['by_category']:
                    financial_data['by_category'][category] = {
                        'income': 0,
                        'expenses': 0,
                        'net': 0,
                        'transactions': []
                    }
                
                if transaction_type.lower() == 'income':
                    financial_data['by_category'][category]['income'] += amount
                else:
                    financial_data['by_category'][category]['expenses'] += amount
                
                financial_data['by_category'][category]['net'] = (
                    financial_data['by_category'][category]['income'] - 
                    financial_data['by_category'][category]['expenses']
                )
                
                financial_data['by_category'][category]['transactions'].append(row)
                
                # Track by account
                if account not in financial_data['by_account']:
                    financial_data['by_account'][account] = {
                        'income': 0,
                        'expenses': 0,
                        'net': 0,
                        'transactions': []
                    }
                
                if transaction_type.lower() == 'income':
                    financial_data['by_account'][account]['income'] += amount
                else:
                    financial_data['by_account'][account]['expenses'] += amount
                
                financial_data['by_account'][account]['net'] = (
                    financial_data['by_account'][account]['income'] - 
                    financial_data['by_account'][account]['expenses']
                )
                
                financial_data['by_account'][account]['transactions'].append(row)
                
                # Process by date/month for time series analysis
                if date_str:
                    try:
                        # Try different date formats
                        try:
                            date = datetime.strptime(date_str, '%Y-%m-%d')
                        except ValueError:
                            try:
                                date = datetime.strptime(date_str, '%m/%d/%Y')
                            except ValueError:
                                date = datetime.strptime(date_str, '%d/%m/%Y')
                                
                        month_key = date.strftime('%Y-%m')
                        quarter_key = f"Q{(date.month-1)//3+1} {date.year}"
                        
                        # Track by month
                        if month_key not in financial_data['by_month']:
                            financial_data['by_month'][month_key] = {
                                'income': 0,
                                'expenses': 0,
                                'net': 0,
                                'transactions': []
                            }
                        
                        if transaction_type.lower() == 'income':
                            financial_data['by_month'][month_key]['income'] += amount
                        else:
                            financial_data['by_month'][month_key]['expenses'] += amount
                        
                        financial_data['by_month'][month_key]['net'] = (
                            financial_data['by_month'][month_key]['income'] - 
                            financial_data['by_month'][month_key]['expenses']
                        )
                        
                        financial_data['by_month'][month_key]['transactions'].append(row)
                        
                        # Track by quarter
                        if quarter_key not in financial_data['quarters']:
                            financial_data['quarters'][quarter_key] = {
                                'income': 0,
                                'expenses': 0,
                                'net': 0,
                                'transactions': []
                            }
                        
                        if transaction_type.lower() == 'income':
                            financial_data['quarters'][quarter_key]['income'] += amount
                        else:
                            financial_data['quarters'][quarter_key]['expenses'] += amount
                        
                        financial_data['quarters'][quarter_key]['net'] = (
                            financial_data['quarters'][quarter_key]['income'] - 
                            financial_data['quarters'][quarter_key]['expenses']
                        )
                        
                        financial_data['quarters'][quarter_key]['transactions'].append(row)
                    except ValueError:
                        logger.warning(f"Could not parse date: {date_str}")
            except Exception as row_error:
                logger.warning(f"Error processing row: {row} - {str(row_error)}")
                continue
        
        # Calculate net income
        financial_data['net_income'] = financial_data['income'] - financial_data['expenses']
        
        return financial_data
    
    except Exception as e:
        logger.error(f"Error analyzing CSV data: {str(e)}")
        return None

def generate_balance_sheet(financial_data):
    """
    Generate a balance sheet from the analyzed financial data
    
    Args:
        financial_data: Structured financial data
        
    Returns:
        dict: Balance sheet report
    """
    try:
        if not financial_data:
            logger.error("No financial data provided for balance sheet")
            return None
        
        logger.debug(f"Generating balance sheet from data: {type(financial_data)}")
        
        # Extract data for balance sheet calculation
        accounts = financial_data.get('by_account', {})
        
        # Calculate assets and liabilities
        current_assets = {}
        non_current_assets = {}
        current_liabilities = {}
        long_term_liabilities = {}
        
        # Cash accounts are typically considered current assets
        for account_name, account_data in accounts.items():
            # Debug log the account data to see what we're working with
            logger.debug(f"Processing account: {account_name}, data: {type(account_data)}")
            
            # Make sure we're dealing with a proper number for net, not a dict
            net_value = account_data.get('net', 0)
            if not isinstance(net_value, (int, float)):
                # If it's not a number, force it to be a safe value
                logger.warning(f"Account {account_name} net value is not a number: {type(net_value)} - {net_value}")
                # Try to extract a value if it's a dict
                if isinstance(net_value, dict) and 'net' in net_value:
                    net_value = net_value.get('net', 0)
                else:
                    net_value = 0
            
            # Now categorize the account based on its name
            if 'cash' in account_name.lower() or 'bank' in account_name.lower() or 'savings' in account_name.lower():
                current_assets[account_name] = max(0, net_value)  # Only consider positive values as assets
            elif 'receivable' in account_name.lower():
                current_assets[account_name] = max(0, net_value)
            elif 'equipment' in account_name.lower() or 'investment' in account_name.lower():
                non_current_assets[account_name] = max(0, net_value)
            elif 'credit card' in account_name.lower():
                # Credit cards typically have negative balances when there's debt
                if net_value < 0:
                    current_liabilities[account_name] = -net_value  # Convert to positive for liabilities
                else:
                    current_assets[account_name] = net_value  # A positive credit card balance is an asset
            else:
                # Default to current assets if we can't determine and value is positive
                if net_value > 0:
                    current_assets[account_name] = net_value
        
        # Calculate totals
        total_current_assets = sum(current_assets.values())
        total_non_current_assets = sum(non_current_assets.values())
        total_assets = total_current_assets + total_non_current_assets
        
        # Process additional accounts for liabilities (beyond what we've already done in the assets section)
        for account_name, account_data in accounts.items():
            # Skip accounts we've already processed
            if (account_name in current_assets or 
                account_name in non_current_assets or 
                account_name in current_liabilities):
                continue
                
            # Ensure net value is a number
            net_value = account_data.get('net', 0)
            if not isinstance(net_value, (int, float)):
                if isinstance(net_value, dict) and 'net' in net_value:
                    net_value = net_value.get('net', 0)
                else:
                    logger.warning(f"Account {account_name} net value is not a number: {type(net_value)}")
                    net_value = 0
                
            # Only add to liabilities if the name suggests a liability and the value is negative
            if 'payable' in account_name.lower() or 'loan' in account_name.lower() or 'debt' in account_name.lower():
                if net_value < 0:
                    current_liabilities[account_name] = -net_value  # Convert to positive for liabilities
                    
            # If negative value but not clearly categorized, assume it's a liability
            elif net_value < 0:
                # If it doesn't clearly fit elsewhere, categorize based on negative value
                current_liabilities[f"Other liability ({account_name})"] = -net_value
        
        # For long term debt, look at transactions with debt-related categories
        categories = financial_data.get('by_category', {})
        for category_name, category_data in categories.items():
            # Debug log to see what we're processing
            logger.debug(f"Processing category: {category_name}, data: {type(category_data)}")
            
            # Ensure net value is a number
            category_net = category_data.get('net', 0)
            if not isinstance(category_net, (int, float)):
                if isinstance(category_net, dict) and 'net' in category_net:
                    category_net = category_net.get('net', 0)
                else:
                    logger.warning(f"Category {category_name} net value is not a number: {type(category_net)}")
                    category_net = 0
                
            if any(term in category_name.lower() for term in ['loan', 'debt', 'mortgage']):
                # Assume it's a long-term liability
                if category_net < 0:
                    long_term_liabilities[category_name] = -category_net  # Convert to positive for liabilities
                else:
                    long_term_liabilities[category_name] = 0
        
        # Calculate totals
        total_current_liabilities = sum(current_liabilities.values())
        total_long_term_liabilities = sum(long_term_liabilities.values())
        total_liabilities = total_current_liabilities + total_long_term_liabilities
        
        # Calculate equity (Assets - Liabilities)
        equity = total_assets - total_liabilities
        
        # Log the final calculated values
        logger.debug(f"Balance Sheet Totals - Assets: {total_assets}, Liabilities: {total_liabilities}, Equity: {equity}")
        
        # Create balance sheet structure
        balance_sheet = {
            'assets': {
                'current_assets': current_assets,
                'non_current_assets': non_current_assets,
                'total': total_assets
            },
            'liabilities': {
                'current_liabilities': current_liabilities,
                'long_term_liabilities': long_term_liabilities,
                'total': total_liabilities
            },
            'equity': {
                'retained_earnings': equity,
                'total': equity
            },
            'total_assets': total_assets,
            'generated_at': datetime.now().isoformat(),
            'insights': generate_balance_sheet_insights(
                total_assets, total_liabilities, equity, current_assets, total_current_liabilities
            )
        }
        
        # Generate recommendations based on the balance sheet insights
        recommendations = []
        if equity > 0 and total_assets > 0:
            ratio = equity / total_assets
            if ratio < 0.3:
                recommendations.append("Consider increasing equity position to improve financial stability.")
            elif ratio > 0.7:
                recommendations.append("Your equity position is strong. Consider growth opportunities.")
            else:
                recommendations.append("Maintain your balanced equity-to-assets ratio.")

        # Add a standard recommendation
        recommendations.append("Review your assets allocation to ensure optimal financial structure.")
        recommendations.append("Regularly compare your balance sheet against industry benchmarks.")
            
        # Create a summary of the financial position
        if total_assets > 0:
            asset_summary = f"Your financial position shows total assets of ${total_assets:,.2f} with "
            if total_liabilities > 0:
                asset_summary += f"liabilities of ${total_liabilities:,.2f} and equity of ${equity:,.2f}."
            else:
                asset_summary += f"minimal liabilities and equity of ${equity:,.2f}."
                
            if total_current_assets > 0 and total_current_liabilities > 0:
                current_ratio = total_current_assets / max(total_current_liabilities, 1)
                if current_ratio > 1.5:
                    asset_summary += f" You have strong liquidity with a current ratio of {current_ratio:.2f}."
                elif current_ratio > 1:
                    asset_summary += f" You have adequate liquidity with a current ratio of {current_ratio:.2f}."
                else:
                    asset_summary += f" Your liquidity may need attention with a current ratio of {current_ratio:.2f}."
        else:
            asset_summary = "No significant assets were found in your financial data."
            
        # Return properly nested structure for template with all the required elements
        return {
            'balance_sheet': balance_sheet,
            'insights': balance_sheet['insights'],  # Add insights at top level for the template
            'recommendations': recommendations,     # Add recommendations for the template
            'summary': asset_summary               # Add summary for the template
        }
    
    except Exception as e:
        logger.error(f"Error generating balance sheet: {str(e)}")
        # Provide error details but also ensure we return a valid structure
        error_message = f"We encountered an error while generating your balance sheet: {str(e)}"
        fallback_insights = [
            "We encountered an error while generating your balance sheet.",
            "This might happen if your financial data doesn't contain typical balance sheet accounts.",
            "Try uploading data with clear account categories like Cash, Receivables, Payables, etc."
        ]
        fallback_recommendations = [
            "Review your financial data format to ensure it includes proper account categories.",
            "Try uploading a different CSV file with standard accounting categorization."
        ]
        
        return {
            'balance_sheet': {
                'assets': {'current_assets': {}, 'non_current_assets': {}, 'total': 0},
                'liabilities': {'current_liabilities': {}, 'long_term_liabilities': {}, 'total': 0},
                'equity': {'retained_earnings': 0, 'total': 0},
                'total_assets': 0,
                'insights': fallback_insights,
                'error': str(e)
            },
            'insights': fallback_insights,
            'recommendations': fallback_recommendations,
            'summary': "Error processing financial data. Please check your data format and try again."
        }

def generate_balance_sheet_insights(assets, liabilities, equity, current_assets, current_liabilities):
    """Generate insights for the balance sheet"""
    insights = []
    
    # Add a general insight
    insights.append(f"Your balance sheet shows total assets of ${assets:,.2f} with liabilities at ${liabilities:,.2f}.")
    
    # Debt to equity ratio
    if equity > 0:
        try:
            debt_to_equity = liabilities / equity
            if debt_to_equity < 0.5:
                insights.append(f"Debt-to-equity ratio is {debt_to_equity:.2f}, indicating low leverage and financial risk.")
            elif debt_to_equity < 1.5:
                insights.append(f"Debt-to-equity ratio is {debt_to_equity:.2f}, which is within a healthy range.")
            else:
                insights.append(f"Debt-to-equity ratio is {debt_to_equity:.2f}, suggesting relatively high leverage.")
        except Exception as e:
            # Add fallback insight in case of calculation error
            insights.append("Debt-to-equity ratio calculation could not be completed with current data.")
    
    # Current ratio
    if current_liabilities > 0:
        try:
            current_assets_sum = sum(current_assets.values())
            current_ratio = current_assets_sum / current_liabilities
            if current_ratio > 2:
                insights.append(f"Current ratio of {current_ratio:.2f} indicates strong short-term liquidity.")
            elif current_ratio > 1:
                insights.append(f"Current ratio of {current_ratio:.2f} shows adequate ability to cover short-term obligations.")
            else:
                insights.append(f"Current ratio of {current_ratio:.2f} suggests possible short-term liquidity challenges.")
            
            insights.append(f"Your current assets of ${current_assets_sum:,.2f} are available to cover your short-term liabilities of ${current_liabilities:,.2f}.")
        except Exception as e:
            # Add fallback insight in case of calculation error
            insights.append("Current ratio calculation could not be completed with current data.")
    
    # Asset composition
    if assets > 0:
        try:
            current_assets_sum = sum(current_assets.values())
            current_assets_pct = current_assets_sum / assets * 100
            insights.append(f"Current assets represent {current_assets_pct:.1f}% of your total assets.")
            
            # Add info about major assets
            if current_assets:
                top_assets = sorted(current_assets.items(), key=lambda x: x[1], reverse=True)[:3]
                insights.append("Your major current assets include: " + ", ".join([f"{name}: ${value:,.2f}" for name, value in top_assets]))
        except Exception as e:
            # Add fallback insight in case of calculation error
            insights.append("Asset composition analysis could not be completed with current data.")
    
    # Equity to assets
    if assets > 0:
        try:
            equity_to_assets = equity / assets * 100
            if equity_to_assets > 50:
                insights.append(f"Equity to assets ratio of {equity_to_assets:.1f}% indicates strong financial position.")
            elif equity_to_assets > 30:
                insights.append(f"Equity to assets ratio of {equity_to_assets:.1f}% shows adequate financial stability.")
            else:
                insights.append(f"Equity to assets ratio of {equity_to_assets:.1f}% suggests higher financial leverage.")
        except Exception as e:
            # Add fallback insight in case of calculation error
            insights.append("Equity to assets ratio calculation could not be completed with current data.")
    
    # Make sure we always return at least some insights
    if not insights:
        insights = [
            "Your balance sheet provides a snapshot of your assets, liabilities, and equity.",
            "Consider reviewing your asset allocation for optimal financial management.",
            "Regular balance sheet analysis helps track your long-term financial health."
        ]
    
    return insights

def generate_income_statement(financial_data):
    """
    Generate an income statement from the analyzed financial data
    
    Args:
        financial_data: Structured financial data
        
    Returns:
        dict: Income statement report
    """
    try:
        if not financial_data:
            logger.error("No financial data provided for income statement")
            return None
        
        # Extract data for income statement
        categories = financial_data.get('by_category', {})
        total_revenue = financial_data.get('income', 0)
        
        # Initialize income statement components
        cost_of_goods_sold = 0
        operating_expenses = {}
        other_income_expenses = {}
        
        # Calculate COGS
        for category_name, category_data in categories.items():
            category_lower = category_name.lower()
            
            # Identify COGS related categories
            if any(term in category_lower for term in ['cogs', 'cost of goods', 'cost of sales', 'inventory']):
                cost_of_goods_sold += category_data['expenses']
            
            # Identify operating expenses
            elif any(term in category_lower for term in [
                'rent', 'salary', 'salaries', 'utilities', 'office', 'marketing', 
                'advertising', 'travel', 'insurance'
            ]):
                operating_expenses[category_name] = category_data['expenses']
            
            # Identify other income/expenses
            elif any(term in category_lower for term in ['interest', 'tax', 'depreciation', 'amortization']):
                other_income_expenses[category_name] = category_data['expenses']
        
        # Calculate totals
        total_operating_expenses = sum(operating_expenses.values())
        total_other_expenses = sum(other_income_expenses.values())
        
        # Calculate profits
        gross_profit = total_revenue - cost_of_goods_sold
        operating_income = gross_profit - total_operating_expenses
        income_before_taxes = operating_income - total_other_expenses
        
        # Estimate taxes (simplified)
        estimated_tax_rate = 0.21  # 21% corporate tax rate
        taxes = income_before_taxes * estimated_tax_rate if income_before_taxes > 0 else 0
        
        # Calculate net income
        net_income = income_before_taxes - taxes
        
        # Create income statement structure
        income_statement = {
            'revenue': total_revenue,
            'cost_of_goods_sold': cost_of_goods_sold,
            'gross_profit': gross_profit,
            'operating_expenses': operating_expenses,
            'operating_income': operating_income,
            'other_income_expenses': other_income_expenses,
            'income_before_taxes': income_before_taxes,
            'taxes': taxes,
            'net_income': net_income,
            'generated_at': datetime.now().isoformat(),
            'insights': generate_income_statement_insights(
                total_revenue, gross_profit, operating_income, net_income
            )
        }
        
        # Generate a summary for the income statement
        summary = f"Your income statement shows total revenue of ${total_revenue:,.2f} with net income of ${net_income:,.2f}."
        
        if total_revenue > 0:
            profit_margin = (net_income / total_revenue) * 100
            summary += f" Your profit margin is {profit_margin:.1f}%."
            
            if profit_margin > 15:
                summary += " This is a strong performance compared to industry averages."
            elif profit_margin > 8:
                summary += " This is a healthy performance within industry norms."
            else:
                summary += " There may be opportunities to improve profitability."
        
        # Add recommendations based on performance
        recommendations = []
        
        if cost_of_goods_sold > 0 and total_revenue > 0:
            cogs_ratio = (cost_of_goods_sold / total_revenue) * 100
            if cogs_ratio > 70:
                recommendations.append("Consider strategies to reduce cost of goods sold, which is currently high relative to revenue.")
            else:
                recommendations.append("Your cost of goods sold is at a good level. Continue monitoring to maintain this efficiency.")
        
        if total_operating_expenses > 0 and total_revenue > 0:
            expense_ratio = (total_operating_expenses / total_revenue) * 100
            if expense_ratio > 30:
                recommendations.append("Look for opportunities to optimize operating expenses, which represent a significant portion of revenue.")
            else:
                recommendations.append("Your operating expense ratio is healthy. Continue with your efficient operations management.")
        
        # Add standard recommendations
        recommendations.append("Compare performance across quarters to identify trends and seasonal patterns.")
        recommendations.append("Review pricing strategy to ensure optimal profit margins across all products/services.")
        
        # Return properly structured report with all components
        return {
            'income_statement': income_statement,
            'insights': income_statement['insights'],
            'recommendations': recommendations,
            'summary': summary
        }
    
    except Exception as e:
        logger.error(f"Error generating income statement: {str(e)}")
        # Create fallback content
        fallback_insights = [
            "We encountered an error while generating your income statement.",
            "This might happen if your financial data doesn't contain standard revenue and expense categories.",
            "Try uploading data with clearer income and expense classifications."
        ]
        
        fallback_recommendations = [
            "Review your financial data format to ensure it includes proper revenue and expense categories.",
            "Try uploading a different CSV file with standard income statement categorization.",
            "Ensure your data includes transaction types (Income/Expense) for proper classification."
        ]
        
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
                'insights': fallback_insights,
                'error': str(e)
            },
            'insights': fallback_insights,
            'recommendations': fallback_recommendations,
            'summary': "Error processing income statement data. Please check your data format and try again."
        }

def generate_income_statement_insights(revenue, gross_profit, operating_income, net_income):
    """Generate insights for the income statement"""
    insights = []
    
    # General revenue insight
    insights.append(f"Your total revenue for the period is ${revenue:,.2f}.")
    
    # Profit insights
    insights.append(f"Your gross profit is ${gross_profit:,.2f}, with operating income at ${operating_income:,.2f} and net income at ${net_income:,.2f}.")
    
    # Profit margins
    try:
        if revenue > 0:
            gross_margin = (gross_profit / revenue) * 100
            operating_margin = (operating_income / revenue) * 100
            net_margin = (net_income / revenue) * 100
            
            insights.append(f"Gross profit margin is {gross_margin:.1f}%.")
            
            if gross_margin > 40:
                insights.append("This is a strong gross margin, indicating efficient production/service delivery.")
            elif gross_margin > 20:
                insights.append("This is an average gross margin for most industries.")
            else:
                insights.append("This gross margin is relatively low, suggesting higher production costs.")
            
            insights.append(f"Operating margin is {operating_margin:.1f}%.")
            
            if operating_margin > 15:
                insights.append("This is a strong operating margin, indicating good operational efficiency.")
            elif operating_margin > 8:
                insights.append("This is an average operating margin for most industries.")
            else:
                insights.append("This operating margin is relatively low, suggesting operational challenges.")
            
            insights.append(f"Net profit margin is {net_margin:.1f}%.")
            
            if net_margin > 10:
                insights.append("This is a strong net margin, indicating overall financial health.")
            elif net_margin > 5:
                insights.append("This is an average net margin for most industries.")
            else:
                insights.append("This net margin is relatively low, suggesting profitability challenges.")
    except Exception as e:
        # Fallback insights if calculations fail
        insights.append("Margin calculations could not be computed with the current data.")
    
    # Add some strategic insights
    if net_income > 0:
        insights.append("Your business is profitable. Consider strategies to increase revenue or reduce costs to further improve your profit margins.")
    else:
        insights.append("Your business is currently operating at a loss. Focus on increasing revenue streams and optimizing your cost structure to achieve profitability.")
    
    # Ensure we have at least some insights
    if len(insights) < 3:
        insights.extend([
            "Regular income statement analysis is crucial for monitoring your business performance.",
            "Compare your current performance with previous periods to identify trends.",
            "Break down your revenue sources to identify which products or services are most profitable."
        ])
    
    return insights

def generate_cash_flow(financial_data):
    """
    Generate a cash flow statement from the analyzed financial data
    
    Args:
        financial_data: Structured financial data
        
    Returns:
        dict: Cash flow statement report
    """
    try:
        if not financial_data:
            logger.error("No financial data provided for cash flow statement")
            return None
        
        # Extract data for cash flow calculation
        transactions = financial_data.get('transactions', [])
        categories = financial_data.get('by_category', {})
        accounts = financial_data.get('by_account', {})
        months = financial_data.get('by_month', {})
        
        # Determine beginning and ending cash
        # Use the first and last months in sorted order
        sorted_months = sorted(months.keys())
        beginning_cash = 0
        ending_cash = 0
        
        if sorted_months:
            # For simplicity, use the first month's income as beginning cash
            first_month = sorted_months[0]
            beginning_cash = sum(
                float(t.get('Amount', 0)) for t in months[first_month]['transactions']
                if t.get('Type', '').lower() == 'income'
            )
            
            # Use the last month's net as ending cash
            last_month = sorted_months[-1]
            ending_cash = beginning_cash + sum(
                float(t.get('Amount', 0)) if t.get('Type', '').lower() == 'income' else -float(t.get('Amount', 0))
                for t in months[last_month]['transactions']
            )
        
        # Initialize cash flow components
        operating_activities = {}
        investing_activities = {}
        financing_activities = {}
        
        # Categorize transactions into cash flow components
        for category_name, category_data in categories.items():
            category_lower = category_name.lower()
            
            # Operating activities
            if any(term in category_lower for term in [
                'revenue', 'income', 'sale', 'commission', 'fee', 'service',
                'rent', 'salary', 'utilities', 'office', 'marketing', 'insurance'
            ]):
                operating_activities[category_name] = category_data['net']
            
            # Investing activities
            elif any(term in category_lower for term in [
                'equipment', 'investment', 'asset', 'property', 'capital', 'research'
            ]):
                investing_activities[category_name] = category_data['net']
            
            # Financing activities
            elif any(term in category_lower for term in [
                'loan', 'debt', 'dividend', 'equity', 'stock', 'financing'
            ]):
                financing_activities[category_name] = category_data['net']
            
            # Default to operating if we can't determine
            else:
                operating_activities[category_name] = category_data['net']
        
        # Calculate totals
        net_cash_from_operating = sum(operating_activities.values())
        net_cash_from_investing = sum(investing_activities.values())
        net_cash_from_financing = sum(financing_activities.values())
        
        # Calculate net change in cash
        net_change_in_cash = net_cash_from_operating + net_cash_from_investing + net_cash_from_financing
        
        # Create cash flow statement structure
        cash_flow_statement = {
            'operating_activities': operating_activities,
            'investing_activities': investing_activities,
            'financing_activities': financing_activities,
            'beginning_cash': beginning_cash,
            'net_cash_from_operating': net_cash_from_operating,
            'net_cash_from_investing': net_cash_from_investing,
            'net_cash_from_financing': net_cash_from_financing,
            'net_change_in_cash': net_change_in_cash,
            'ending_cash': beginning_cash + net_change_in_cash,
            'generated_at': datetime.now().isoformat(),
            'insights': generate_cash_flow_insights(
                net_cash_from_operating, net_cash_from_investing, net_cash_from_financing, net_change_in_cash
            )
        }
        
        # Generate recommendations based on cash flow data
        recommendations = []
        
        # Create a summary of the cash flow statement
        summary = f"Your cash flow statement shows a net change of ${net_change_in_cash:,.2f} for the period."
        
        if net_cash_from_operating > 0:
            summary += f" You have positive operating cash flow of ${net_cash_from_operating:,.2f}, "
            recommendations.append("Maintain your positive operating cash flow by continuing efficient collection and payment practices.")
        else:
            summary += f" Your operating cash flow is ${net_cash_from_operating:,.2f}, "
            recommendations.append("Focus on improving your operating cash flow through better receivables management and cost control.")
        
        # Add info about investing/financing
        if net_cash_from_investing < 0 and abs(net_cash_from_investing) > 0.2 * abs(net_cash_from_operating):
            summary += f"with significant investment activities of ${net_cash_from_investing:,.2f}."
            recommendations.append("Monitor return on your investments to ensure they generate adequate future cash flows.")
        elif net_cash_from_financing != 0:
            summary += f"with financing activities of ${net_cash_from_financing:,.2f}."
            if net_cash_from_financing > 0:
                recommendations.append("Use your new financing strategically to generate positive future cash flows.")
            else:
                recommendations.append("Your debt reduction/dividend payments show financial strength. Continue managing obligations effectively.")
        
        # Add general recommendations
        recommendations.append("Regularly compare your cash flow across periods to identify trends and patterns.")
        recommendations.append("Maintain a cash reserve to handle unexpected financial challenges or opportunities.")
        
        # Return properly structured report with all components
        return {
            'cash_flow_statement': cash_flow_statement,
            'insights': cash_flow_statement['insights'],
            'recommendations': recommendations,
            'summary': summary
        }
    
    except Exception as e:
        logger.error(f"Error generating cash flow: {str(e)}")
        # Create fallback content
        fallback_insights = [
            "We encountered an error while generating your cash flow statement.",
            "This might happen if your financial data doesn't contain proper transaction categorization.",
            "Try uploading data with clearer transaction types and categories."
        ]
        
        fallback_recommendations = [
            "Review your financial data format to ensure transactions have clear categories.",
            "Try uploading a different CSV file with standard cash flow categorization.",
            "Ensure your data includes transaction dates for proper period analysis."
        ]
        
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
                'insights': fallback_insights,
                'error': str(e)
            },
            'insights': fallback_insights,
            'recommendations': fallback_recommendations,
            'summary': "Error processing cash flow data. Please check your data format and try again."
        }

def generate_cash_flow_insights(operating, investing, financing, net_change):
    """Generate insights for the cash flow statement"""
    insights = []
    
    # General overview
    insights.append(f"Your cash flow shows a net change of ${net_change:,.2f} for the period.")
    
    try:
        # Operating cash flow
        if operating > 0:
            insights.append(f"Positive operating cash flow of ${operating:,.2f} indicates healthy core business operations.")
        else:
            insights.append(f"Negative operating cash flow of ${operating:,.2f} may indicate operational challenges.")
        
        # Investing cash flow
        if investing < 0:
            insights.append(f"Negative investing cash flow of ${investing:,.2f} indicates investment in growth.")
        else:
            insights.append(f"Positive investing cash flow of ${investing:,.2f} may indicate selling of assets.")
        
        # Financing cash flow
        if financing > 0:
            insights.append(f"Positive financing cash flow of ${financing:,.2f} indicates raising capital.")
        else:
            insights.append(f"Negative financing cash flow of ${financing:,.2f} indicates debt repayment or dividends.")
        
        # Net change
        if net_change > 0:
            insights.append(f"Overall positive cash flow of ${net_change:,.2f} strengthens your liquidity position.")
        else:
            insights.append(f"Overall negative cash flow of ${net_change:,.2f} may require attention to cash management.")
        
        # Cash flow adequacy
        if operating > 0 and investing < 0:
            coverage = abs(operating / investing) if investing != 0 else float('inf')
            if coverage > 1:
                insights.append(f"Operating cash flow covers {coverage:.1f}x of investing activities, indicating sustainable growth.")
            else:
                insights.append(f"Operating cash flow covers only {coverage:.1f}x of investing activities, suggesting external financing needs.")
    except Exception as e:
        # Fallback insights if calculations fail
        insights.append("Cash flow metric calculations could not be computed with the current data.")
    
    # Strategic insights
    if net_change > 0:
        insights.append("Your positive cash flow position provides opportunities for business expansion, debt reduction, or shareholder returns.")
    else:
        insights.append("Focus on improving cash flow by accelerating collections, managing inventory efficiently, and reviewing payment terms.")
    
    # Add recommendations based on operating cash flow
    if operating > 0:
        insights.append("Your positive operating cash flow is a good indicator of business sustainability. Maintain efficient working capital management.")
    else:
        insights.append("Work on improving your operating cash flow through better receivables management and cost control measures.")
    
    # Ensure we have at least some insights
    if len(insights) < 3:
        insights.extend([
            "Cash flow analysis helps you understand your business's ability to generate and use cash.",
            "Monitor cash flow trends over time to identify seasonal patterns or growth opportunities.",
            "A strong cash position provides flexibility to weather economic downturns."
        ])
    
    return insights

def generate_financial_analysis(financial_data):
    """
    Generate a comprehensive financial analysis from the analyzed financial data
    
    Args:
        financial_data: Structured financial data
        
    Returns:
        dict: Financial analysis report
    """
    try:
        if not financial_data:
            logger.error("No financial data provided for financial analysis")
            return None
        
        # Get components from financial data
        total_revenue = financial_data.get('income', 0)
        total_expenses = financial_data.get('expenses', 0)
        net_income = financial_data.get('net_income', 0)
        categories = financial_data.get('by_category', {})
        accounts = financial_data.get('by_account', {})
        months = financial_data.get('by_month', {})
        quarters = financial_data.get('quarters', {})
        
        # Generate financial metrics
        metrics = {
            'profitability': calculate_profitability_metrics(total_revenue, total_expenses, net_income),
            'liquidity': calculate_liquidity_metrics(accounts),
            'efficiency': calculate_efficiency_metrics(total_revenue, accounts, categories)
        }
        
        # Generate trends
        trends = generate_trends(months, quarters)
        
        # Generate recommendations
        recommendations = generate_recommendations(metrics, trends)
        
        # Create analysis structure
        analysis = {
            'summary': generate_summary(metrics, trends),
            'key_metrics': metrics,
            'trends': trends,
            'recommendations': recommendations,
            'generated_at': datetime.now().isoformat()
        }
        
        # Return properly nested structure for template
        return {
            'analysis': analysis
        }
    
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

def calculate_profitability_metrics(revenue, expenses, net_income):
    """Calculate profitability metrics"""
    metrics = {}
    
    if revenue > 0:
        # Profit margin
        metrics['net_margin'] = net_income / revenue
        
        # Gross margin (simplified)
        estimated_cogs = expenses * 0.6  # Estimate COGS as 60% of expenses
        gross_profit = revenue - estimated_cogs
        metrics['gross_margin'] = gross_profit / revenue
        
        # Operating margin
        operating_expenses = expenses - estimated_cogs
        operating_income = gross_profit - operating_expenses
        metrics['operating_margin'] = operating_income / revenue
    
    return metrics

def calculate_liquidity_metrics(accounts):
    """Calculate liquidity metrics"""
    metrics = {}
    
    # Extract current assets and liabilities
    current_assets = sum(
        account_data['net'] for account_name, account_data in accounts.items()
        if any(term in account_name.lower() for term in ['cash', 'bank', 'receivable'])
    )
    
    current_liabilities = sum(
        -account_data['net'] for account_name, account_data in accounts.items()
        if any(term in account_name.lower() for term in ['payable']) and account_data['net'] < 0
    )
    
    # Cash and cash equivalents
    cash = sum(
        account_data['net'] for account_name, account_data in accounts.items()
        if any(term in account_name.lower() for term in ['cash', 'bank'])
    )
    
    # Calculate ratios
    if current_liabilities > 0:
        metrics['current_ratio'] = current_assets / current_liabilities
        metrics['cash_ratio'] = cash / current_liabilities
    
    return metrics

def calculate_efficiency_metrics(revenue, accounts, categories):
    """Calculate efficiency metrics"""
    metrics = {}
    
    # Total assets (simplified)
    total_assets = sum(
        account_data['net'] for account_name, account_data in accounts.items()
        if account_data['net'] > 0
    )
    
    # Asset turnover
    if total_assets > 0:
        metrics['asset_turnover'] = revenue / total_assets
    
    return metrics

def generate_trends(months, quarters):
    """Generate financial trends"""
    trends = []
    
    # Sort months and quarters chronologically
    sorted_months = sorted(months.keys())
    sorted_quarters = sorted(quarters.keys())
    
    # Analyze revenue trends
    if len(sorted_months) > 1:
        first_month = sorted_months[0]
        last_month = sorted_months[-1]
        
        first_month_income = months[first_month]['income']
        last_month_income = months[last_month]['income']
        
        if first_month_income > 0:
            revenue_change = (last_month_income - first_month_income) / first_month_income * 100
            trends.append(f"Revenue has {'increased' if revenue_change > 0 else 'decreased'} by {abs(revenue_change):.1f}% over the period.")
    
    # Analyze quarterly trends
    if len(sorted_quarters) > 1:
        quarters_income = [quarters[q]['income'] for q in sorted_quarters]
        quarters_expenses = [quarters[q]['expenses'] for q in sorted_quarters]
        
        # Identify income trend
        income_trend = 'stable'
        if all(quarters_income[i] > quarters_income[i-1] for i in range(1, len(quarters_income))):
            income_trend = 'consistently increasing'
        elif all(quarters_income[i] < quarters_income[i-1] for i in range(1, len(quarters_income))):
            income_trend = 'consistently decreasing'
        elif quarters_income[-1] > quarters_income[0]:
            income_trend = 'generally increasing'
        elif quarters_income[-1] < quarters_income[0]:
            income_trend = 'generally decreasing'
        
        trends.append(f"Quarterly revenue shows a {income_trend} trend.")
        
        # Analyze expense to income ratio
        expense_to_income = [expenses/income if income > 0 else float('inf') for income, expenses in zip(quarters_income, quarters_expenses)]
        
        if len(expense_to_income) > 1 and expense_to_income[0] != float('inf') and expense_to_income[-1] != float('inf'):
            ratio_change = expense_to_income[-1] - expense_to_income[0]
            if abs(ratio_change) > 0.05:  # 5% change threshold
                trends.append(f"Expense-to-income ratio has {'increased' if ratio_change > 0 else 'decreased'} from {expense_to_income[0]:.2f} to {expense_to_income[-1]:.2f}.")
    
    # Add default trend if none found
    if not trends:
        trends.append("Insufficient time-series data to establish clear trends.")
    
    return trends

def generate_recommendations(metrics, trends):
    """Generate financial recommendations"""
    recommendations = []
    
    # Standard recommendations that should always be included
    standard_recommendations = [
        "Regularly review your financial performance against industry benchmarks.",
        "Maintain detailed financial records to track your business's financial health over time."
    ]
    
    try:
        # Profitability recommendations
        profitability = metrics.get('profitability', {})
        if 'net_margin' in profitability:
            net_margin = profitability['net_margin']
            if net_margin < 0.05:
                recommendations.append("Focus on improving net margin through cost control and pricing strategy.")
                recommendations.append("Analyze your product/service mix to identify and grow high-margin offerings.")
            elif net_margin < 0.1:
                recommendations.append("Consider strategic initiatives to enhance profit margins.")
                recommendations.append("Explore opportunities to streamline operations and reduce overhead costs.")
            else:
                recommendations.append("Maintain your strong profit margins by continuing to monitor costs and pricing.")
        
        # Liquidity recommendations
        liquidity = metrics.get('liquidity', {})
        if 'current_ratio' in liquidity:
            current_ratio = liquidity['current_ratio']
            if current_ratio < 1:
                recommendations.append("Improve short-term liquidity to better cover current obligations.")
                recommendations.append("Consider negotiating extended payment terms with suppliers or accelerating customer collections.")
            elif current_ratio > 3:
                recommendations.append("Consider utilizing excess liquid assets for growth opportunities or shareholder returns.")
                recommendations.append("Review your cash management strategy to ensure idle funds are earning competitive returns.")
            else:
                recommendations.append("Your liquidity position is balanced. Continue monitoring cash flow regularly.")
        
        # Efficiency recommendations
        efficiency = metrics.get('efficiency', {})
        if 'asset_turnover' in efficiency:
            asset_turnover = efficiency['asset_turnover']
            if asset_turnover < 0.5:
                recommendations.append("Evaluate asset utilization to improve revenue generation efficiency.")
                recommendations.append("Consider divesting underperforming assets or finding ways to increase their productivity.")
            else:
                recommendations.append("Your asset efficiency is strong. Continue leveraging assets effectively for revenue generation.")
    except Exception as e:
        # Add generic recommendations if metric-based ones fail
        recommendations.append("Review your revenue streams and cost structure to identify opportunities for improvement.")
        recommendations.append("Conduct a detailed analysis of your expenses to identify potential cost-saving opportunities.")
    
    # Add trend-based recommendations
    if trends and len(trends) > 0:
        if "increasing" in trends[0].lower():
            recommendations.append("Capitalize on your positive growth trend by reinvesting in business expansion.")
        elif "decreasing" in trends[0].lower():
            recommendations.append("Address the declining trend by evaluating market conditions and adjusting your business strategy.")
        else:
            recommendations.append("While performance is stable, explore new markets or products to drive future growth.")
    
    # Include the standard recommendations
    recommendations.extend(standard_recommendations)
    
    # Ensure we have at least a minimum number of recommendations
    if len(recommendations) < 4:
        additional_recommendations = [
            "Build a financial forecast to anticipate future cash needs and opportunities.",
            "Review your pricing strategy to ensure it aligns with market conditions and costs.",
            "Diversify revenue streams to mitigate risk and create multiple growth avenues.",
            "Implement regular financial reviews to catch issues early and capitalize on opportunities."
        ]
        recommendations.extend(additional_recommendations[:4-len(recommendations)])
    
    return recommendations

def generate_summary(metrics, trends):
    """Generate financial summary"""
    # Create a concise summary
    profitability = metrics.get('profitability', {})
    liquidity = metrics.get('liquidity', {})
    efficiency = metrics.get('efficiency', {})
    
    summary_parts = []
    
    try:
        # Overall financial health statement
        summary_parts.append("Based on the analysis of your financial data")
        
        # Profitability summary
        if 'net_margin' in profitability:
            net_margin = profitability['net_margin']
            if net_margin > 0.1:
                summary_parts.append("your business shows strong profitability with a net margin above 10%")
            elif net_margin > 0.05:
                summary_parts.append("your business has adequate profitability with a net margin between 5-10%")
            elif net_margin > 0:
                summary_parts.append("your business has marginal profitability with a net margin below 5%")
            else:
                summary_parts.append("your business is currently operating at a loss")
        
        # Liquidity summary
        if 'current_ratio' in liquidity:
            current_ratio = liquidity['current_ratio']
            if current_ratio > 2:
                summary_parts.append("you maintain healthy liquidity with a strong current ratio above 2")
            elif current_ratio > 1:
                summary_parts.append("you have adequate liquidity with a current ratio above 1")
            else:
                summary_parts.append("you have limited liquidity which may impact short-term obligations")
        
        # Efficiency summary
        if 'asset_turnover' in efficiency:
            asset_turnover = efficiency['asset_turnover']
            if asset_turnover > 1:
                summary_parts.append("your asset utilization is excellent")
            elif asset_turnover > 0.5:
                summary_parts.append("your asset utilization is adequate")
            else:
                summary_parts.append("your asset utilization could be improved")
        
        # Trend summary
        if trends:
            if any("increasing" in trend.lower() for trend in trends[:2]):
                summary_parts.append("the business shows a positive growth trend")
            elif any("decreasing" in trend.lower() for trend in trends[:2]):
                summary_parts.append("the business shows a declining trend requiring attention")
            else:
                summary_parts.append("overall performance appears stable")
    except Exception as e:
        # Provide a simple summary if calculations fail
        return "Financial analysis completed based on your financial data. Review the detailed reports for specific insights."
    
    # Format the summary
    if len(summary_parts) > 1:
        # First part is the intro
        intro = summary_parts[0]
        details = summary_parts[1:]
        
        # Join with commas and end with period
        formatted_details = ", ".join(details)
        return f"{intro}, {formatted_details}."
    else:
        return "Financial analysis completed based on the provided data. Review the detailed reports for specific insights."