import os
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fintelligence_demo'

# DEMO DATA
BALANCE_SHEET = {
    'balance_sheet': {
        'assets': {
            'current_assets': {
                'cash': 125000,
                'accounts_receivable': 75000,
                'inventory': 50000
            },
            'non_current_assets': {
                'property_and_equipment': 200000,
                'investments': 100000
            },
            'total': 550000
        },
        'liabilities': {
            'current_liabilities': {
                'accounts_payable': 45000,
                'short_term_debt': 30000
            },
            'long_term_liabilities': {
                'long_term_debt': 150000
            },
            'total': 225000
        },
        'equity': {
            'retained_earnings': 225000,
            'common_stock': 100000,
            'total': 325000
        },
        'total_assets': 550000,
        'insights': [
            "The company has a strong cash position, representing about 23% of total assets.",
            "Long-term debt makes up the majority of liabilities at 67%.",
            "The equity to assets ratio is 59%, indicating a relatively strong financial position."
        ]
    }
}

INCOME_STATEMENT = {
    'income_statement': {
        'revenue': 500000,
        'cost_of_goods_sold': 300000,
        'gross_profit': 200000,
        'operating_expenses': {
            'sales_and_marketing': 50000,
            'general_and_administrative': 40000,
            'research_and_development': 30000
        },
        'operating_income': 80000,
        'other_income_expenses': {
            'interest_expense': 10000
        },
        'income_before_taxes': 70000,
        'taxes': 15000,
        'net_income': 55000,
        'insights': [
            "The company has a gross profit margin of 40%, which is strong.",
            "Operating expenses consume 24% of revenue.",
            "The net profit margin is 11%, which is good for this industry."
        ]
    }
}

CASH_FLOW = {
    'cash_flow_statement': {
        'operating_activities': {
            'net_income': 55000,
            'depreciation': 20000,
            'changes_in_working_capital': -15000,
            'total': 60000
        },
        'investing_activities': {
            'capital_expenditures': -40000,
            'investments': -20000,
            'total': -60000
        },
        'financing_activities': {
            'debt_repayment': -20000,
            'dividends': -10000,
            'total': -30000
        },
        'beginning_cash': 150000,
        'net_cash_from_operating': 60000,
        'net_cash_from_investing': -60000,
        'net_cash_from_financing': -30000,
        'net_change_in_cash': -30000,
        'ending_cash': 120000,
        'insights': [
            "Strong operating cash flow covers capital expenditures.",
            "The company is investing significantly in growth.",
            "Cash position remains healthy despite dividend payments and debt reduction."
        ]
    }
}

ANALYSIS = {
    'analysis': {
        'summary': "The company demonstrates strong financial health with good profitability and cash flow.",
        'key_metrics': {
            'profitability': {
                'gross_margin': 0.4,
                'net_margin': 0.11,
                'return_on_assets': 0.1
            },
            'liquidity': {
                'current_ratio': 2.8,
                'quick_ratio': 2.2,
                'cash_ratio': 1.4
            },
            'efficiency': {
                'asset_turnover': 0.9,
                'inventory_turnover': 6.0,
                'days_sales_outstanding': 45
            }
        },
        'trends': [
            "Revenue growth has been steady at approximately 8-10% annually.",
            "Profit margins have improved by 2 percentage points over the last year.",
            "Cash reserves have slightly decreased due to investments in growth."
        ],
        'recommendations': [
            "Consider optimizing inventory levels to improve cash flow.",
            "Evaluate opportunities to reduce days sales outstanding.",
            "Maintain the current debt-to-equity ratio which provides good leverage."
        ]
    }
}

@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/demo/balance_sheet')
def demo_balance_sheet():
    return render_template('balance_sheet.html', data=BALANCE_SHEET)

@app.route('/demo/income_statement')
def demo_income_statement():
    return render_template('income_statement.html', data=INCOME_STATEMENT)

@app.route('/demo/cash_flow')
def demo_cash_flow():
    return render_template('cash_flow.html', data=CASH_FLOW)

@app.route('/demo/analysis')
def demo_analysis():
    return render_template('financial_analysis.html', data=ANALYSIS)

@app.route('/demo/all')
def demo_all():
    all_data = {
        'balance_sheet': BALANCE_SHEET,
        'income_statement': INCOME_STATEMENT,
        'cash_flow': CASH_FLOW,
        'analysis': ANALYSIS
    }
    return jsonify(all_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)