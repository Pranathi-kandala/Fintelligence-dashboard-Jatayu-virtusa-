"""
Helper script to run Fintelligence locally on Windows
"""
import os
import sys

def check_requirements():
    """Check if the necessary packages are installed"""
    try:
        import flask
        import flask_login
        import flask_sqlalchemy
        import flask_wtf
        import google.generativeai
        import pandas
        import psycopg2
        import sqlalchemy
        print("✓ All required core packages are installed")
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install dependencies using: pip install -r requirements_local.txt")
        sys.exit(1)

def check_environment_vars():
    """Check if the necessary environment variables are set"""
    required_vars = ['DATABASE_URL', 'GEMINI_API_KEY']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set them before running the application.")
        print("Example (in Windows CMD):")
        print('  set DATABASE_URL=postgresql://username:password@localhost:5432/fintelligence')
        print('  set GEMINI_API_KEY=your_gemini_api_key')
        print("Example (in PowerShell):")
        print('  $env:DATABASE_URL = "postgresql://username:password@localhost:5432/fintelligence"')
        print('  $env:GEMINI_API_KEY = "your_gemini_api_key"')
        sys.exit(1)
    else:
        print("✓ All required environment variables are set")

def setup_database():
    """Create database tables if they don't exist"""
    try:
        # First make sure the instance directory exists
        instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
        os.makedirs(instance_dir, exist_ok=True)
        
        # Import app and db only after ensuring the instance directory exists
        from app import app, db
        
        # Create database tables
        with app.app_context():
            db.create_all()
            
        print("✓ Database tables created successfully")
        print(f"  Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def run_app():
    """Run the Flask application"""
    try:
        from main import app
        port = int(os.environ.get('PORT', 5000))
        print(f"Starting Fintelligence on http://localhost:{port}")
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        print(f"❌ Error running application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Fintelligence - Local Setup")
    print("==========================")
    
    check_requirements()
    check_environment_vars()
    setup_database()
    run_app()