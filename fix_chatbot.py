"""
Script to modify the AI processor to use local responses when Gemini API is unavailable
"""
import os
import sys
import re

def modify_ai_processor():
    """Modify the AI processor to handle quota limits better"""
    ai_processor_path = "ai_processor.py"
    
    if not os.path.exists(ai_processor_path):
        print(f"❌ Could not find {ai_processor_path}")
        return False
        
    with open(ai_processor_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Add a local response function to handle common financial queries
    if "def get_local_response" not in content:
        # Find the position to insert the function - after imports but before other functions
        import_pattern = r'(import.*?\n\n)'
        match = re.search(import_pattern, content, re.DOTALL)
        if not match:
            print("❌ Could not find a suitable insertion point for the local response function")
            return False
            
        insertion_point = match.end()
        
        local_response_func = """
# Local response function for when API is unavailable
def get_local_response(query):
    """Generate a helpful response without using the API"""
    query = query.lower()
    
    # Check for common financial terms and questions
    if any(term in query for term in ["what is balance sheet", "explain balance sheet"]):
        return """A balance sheet is a financial statement that shows what a company owns (assets), what it owes (liabilities), and the difference (equity) at a specific point in time. It follows the accounting equation: Assets = Liabilities + Equity.

Key components:
- Assets: Resources owned by the company (cash, inventory, property)
- Liabilities: Obligations and debts owed to others
- Equity: Owners' stake in the business (assets minus liabilities)

The balance sheet provides a snapshot of a company's financial position at a moment in time."""
    
    elif any(term in query for term in ["what is income statement", "explain income statement", "profit and loss", "p&l"]):
        return """An income statement (also called profit and loss statement) shows a company's revenues, expenses, and profit/loss over a specific period of time.

Key components:
- Revenue: Money earned from business activities
- Expenses: Costs incurred to run the business
- Net Income/Loss: The difference between revenue and expenses

The income statement follows the formula: Revenue - Expenses = Profit (or Loss). It helps track business performance over time."""
    
    elif any(term in query for term in ["what is cash flow", "explain cash flow", "cashflow statement"]):
        return """A cash flow statement tracks the movement of money in and out of a business over a specific period. It's crucial for understanding liquidity and financial health.

It has three main sections:
1. Operating Activities: Cash from core business operations
2. Investing Activities: Cash from buying/selling assets
3. Financing Activities: Cash from loans, investors, dividends

Positive cash flow means more money coming in than going out, which is essential for business sustainability."""
    
    elif any(term in query for term in ["ratio", "financial ratio"]):
        return """Financial ratios help analyze a company's performance and financial health. Common ratios include:

1. Liquidity Ratios: Measure ability to pay short-term obligations
   - Current Ratio = Current Assets ÷ Current Liabilities
   - Quick Ratio = (Current Assets - Inventory) ÷ Current Liabilities

2. Profitability Ratios: Measure earnings relative to resources
   - Profit Margin = Net Income ÷ Revenue
   - Return on Assets (ROA) = Net Income ÷ Total Assets
   - Return on Equity (ROE) = Net Income ÷ Shareholders' Equity

3. Efficiency Ratios: Measure how effectively assets are used
   - Inventory Turnover = Cost of Goods Sold ÷ Average Inventory
   - Accounts Receivable Turnover = Net Credit Sales ÷ Average Accounts Receivable"""
    
    elif any(term in query for term in ["profit margin", "increase profit"]):
        return """To improve profit margins, consider these strategies:

1. Increase Revenue:
   - Raise prices strategically
   - Upsell and cross-sell to existing customers
   - Expand to new markets or customer segments

2. Reduce Costs:
   - Optimize supply chain and negotiate with suppliers
   - Improve operational efficiency
   - Reduce overhead expenses

3. Improve Product Mix:
   - Focus on high-margin products or services
   - Phase out underperforming offerings
   - Develop new offerings with higher margins

4. Control Expenses:
   - Implement budgeting and expense tracking
   - Automate repetitive tasks
   - Consider outsourcing non-core functions"""
    
    elif any(term in query for term in ["debt", "leverage", "borrow"]):
        return """Managing debt is crucial for financial health. Some key considerations:

1. Good Debt vs. Bad Debt:
   - Good debt: Generates future value (e.g., business loans for growth)
   - Bad debt: Finances depreciating assets or consumption

2. Important Debt Metrics:
   - Debt-to-Equity Ratio = Total Debt ÷ Total Equity
   - Debt Service Coverage Ratio = Operating Income ÷ Total Debt Service
   - Interest Coverage Ratio = EBIT ÷ Interest Expenses

3. Debt Management Strategies:
   - Refinance high-interest debt
   - Establish clear repayment plans
   - Maintain emergency reserves
   - Consider debt consolidation when appropriate"""
    
    elif any(term in query for term in ["budget", "budgeting", "forecast"]):
        return """Effective budgeting is essential for financial planning:

1. Budget Creation Process:
   - Review historical financial data
   - Set realistic revenue and expense projections
   - Account for seasonality and market trends
   - Include contingency provisions

2. Types of Budgets:
   - Operating Budget: Day-to-day business activities
   - Capital Budget: Long-term investments
   - Cash Flow Budget: Expected cash inflows and outflows
   - Master Budget: Comprehensive financial plan

3. Best Practices:
   - Review and adjust regularly
   - Involve key stakeholders
   - Use zero-based budgeting for greater accountability
   - Track variances between budget and actual performance"""
    
    elif any(term in query for term in ["tax", "taxes", "taxation"]):
        return """Tax planning is an important aspect of financial management:

1. Tax Deductions:
   - Business expenses must be ordinary and necessary
   - Document all deductions thoroughly
   - Common deductions: office expenses, travel, professional services

2. Tax Planning Strategies:
   - Time income and expenses strategically
   - Consider business structure implications
   - Maximize retirement contributions
   - Take advantage of depreciation

3. Tax Compliance:
   - Meet all filing deadlines
   - Keep records for the required retention period
   - Consider working with a tax professional
   - Stay informed about tax law changes"""
    
    else:
        return """I apologize, but I'm currently operating in offline mode due to API quota limitations. 

I can answer basic questions about financial statements (balance sheet, income statement, cash flow), financial ratios, profit improvement, debt management, budgeting, and taxes.

Please try asking a more specific question about one of these financial topics, and I'll do my best to provide a helpful response based on my pre-programmed knowledge."""
"""
        
        # Insert the function into the content
        modified_content = content[:insertion_point] + local_response_func + content[insertion_point:]
        
        # Now modify the process_chat_query function to use the local response function when API fails
        process_chat_pattern = r'def process_chat_query\(user_query, file_data\):.*?try:.*?ai_response = call_gemini_chat\(prompt\)'
        replacement = """def process_chat_query(user_query, file_data):
    """
    Process a user query about financial data using Gemini AI
    
    Args:
        user_query (str): User's financial question
        file_data (list): List of dictionaries containing file data and reports
        
    Returns:
        str: AI response to user query
    """
    try:
        # Check if we have an internet connection and valid API key
        import socket
        has_internet = False
        try:
            # Try to reach Google's DNS server
            socket.create_connection(("8.8.8.8", 53), timeout=1)
            has_internet = True
        except OSError:
            # No internet connection
            pass
            
        if not has_internet or not gemini_api_key or len(gemini_api_key) < 20:
            # Generate a local response without using the API
            return get_local_response(user_query)
            
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
                financial_context = f\"""
                Financial data context:
                - Total Revenue: ${income:,.2f}
                - Total Expenses: ${expenses:,.2f}
                - Net Income: ${net_income:,.2f}
                \"""
                
                # Add account information
                accounts = financial_data.get('by_account', {})
                if accounts:
                    financial_context += "- Top Account Balances:\\n"
                    top_accounts = sorted(accounts.items(), key=lambda x: abs(x[1].get('net', 0) if isinstance(x[1], dict) else 0), reverse=True)[:3]
                    for acct, data in top_accounts:
                        net_value = data.get('net', 0) if isinstance(data, dict) else 0
                        financial_context += f"  * {acct}: ${net_value:,.2f}\\n"
                
                # Add category information
                categories = financial_data.get('by_category', {})
                if categories:
                    top_expenses = {}
                    for cat, data in categories.items():
                        if isinstance(data, dict) and data.get('expenses', 0) > 0:
                            top_expenses[cat] = data.get('expenses', 0)
                    
                    if top_expenses:
                        financial_context += "- Top Expense Categories:\\n"
                        for cat, amt in sorted(top_expenses.items(), key=lambda x: x[1], reverse=True)[:3]:
                            financial_context += f"  * {cat}: ${amt:,.2f}\\n"
        
        # Create appropriate prompt for Gemini based on whether we have financial data
        if financial_context:
            prompt = f\"""I'd like you to answer this financial question: "{user_query}"

Here's the relevant financial data:
{financial_context}

Please provide a helpful, accurate response based on this data. If this is asking about specifics that aren't in the data, focus on the information provided.\"""
        else:
            prompt = f\"""I'd like you to answer this financial question: "{user_query}"

Please explain this concept clearly, even though I don't have specific financial data to share. Provide a helpful explanation using simple terms.\"""
        
        # Try to use the API, but fall back to local response if it fails
        try:
            # Call Gemini API for the response
            ai_response = call_gemini_chat(prompt)
            
            # If we got an error response, use local fallback
            if "429" in ai_response or "quota" in ai_response.lower() or "error" in ai_response.lower():
                return get_local_response(user_query)
                
            return ai_response
        except Exception as api_error:
            logger.warning(f"API call failed, using local response instead: {str(api_error)}")
            return get_local_response(user_query)"""
            
        modified_content = re.sub(process_chat_pattern, replacement, modified_content, flags=re.DOTALL)
        
        # Write the modified content back to the file
        with open(ai_processor_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
            
        print(f"✓ Added local response capability to {ai_processor_path}")
        return True
    else:
        print(f"✓ Local response function already exists in {ai_processor_path}")
        return True

if __name__ == "__main__":
    print("Fixing Chatbot to Work Without API")
    print("=================================")
    
    if modify_ai_processor():
        print("\n✓ Successfully modified AI processor to work without API")
        print("\nYour chatbot can now function even when the Gemini API is unavailable or has quota limits.")
        print("Try using the chatbot again - it should provide helpful responses about finance topics.")
    else:
        print("\n❌ Failed to modify AI processor")
        print("Please check the error messages above.")