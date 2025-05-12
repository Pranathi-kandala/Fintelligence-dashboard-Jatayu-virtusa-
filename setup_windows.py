"""
Interactive setup script for Fintelligence on Windows
"""
import os
import sys
import subprocess
import time
import random
import string
from pathlib import Path

# ANSI colors for Windows
try:
    import colorama
    colorama.init()
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
except ImportError:
    GREEN = YELLOW = RED = BLUE = RESET = BOLD = ''

def print_header(text):
    """Print formatted header"""
    print(f"\n{BOLD}{BLUE}=== {text} ==={RESET}")

def print_success(text):
    """Print success message"""
    print(f"{GREEN}✓ {text}{RESET}")

def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}! {text}{RESET}")

def print_error(text):
    """Print error message"""
    print(f"{RED}✗ {text}{RESET}")

def run_command(command, error_msg="Command failed"):
    """Run a command and return True if successful"""
    try:
        subprocess.run(command, check=True, shell=True)
        return True
    except subprocess.CalledProcessError:
        print_error(error_msg)
        return False

def install_python_dependencies():
    """Install required Python packages"""
    print_header("Installing Required Packages")
    
    # Try to install packages
    packages = [
        "flask", "flask-login", "flask-sqlalchemy", "flask-wtf",
        "google-generativeai", "pytz", "werkzeug", "email-validator",
        "jinja2", "markupsafe", "gunicorn", "psycopg2-binary",
        "sqlalchemy", "pandas", "xhtml2pdf", "trafilatura", 
        "numpy", "openpyxl", "pypdf2", "python-dotenv"
    ]
    
    print("Installing packages. This may take a few minutes...")
    successful = run_command(
        f"{sys.executable} -m pip install {' '.join(packages)}",
        "Failed to install required packages."
    )
    
    if successful:
        print_success("Required packages installed successfully")
    
    return successful

def setup_directories():
    """Create required directories"""
    print_header("Setting Up Directories")
    
    directories = ["instance", "temp", "uploads", "static", "templates"]
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            try:
                path.mkdir(exist_ok=True)
                print_success(f"Created directory: {directory}")
            except Exception as e:
                print_error(f"Failed to create directory {directory}: {e}")
                return False
        else:
            print_success(f"Directory exists: {directory}")
    
    return True

def setup_database():
    """Setup the database connection"""
    print_header("Setting Up Database")
    
    print("Database options:")
    print("1. Neon PostgreSQL (cloud-hosted, no local installation)")
    print("2. SQLite (simple, local file-based database)")
    print("3. Local PostgreSQL (if you already have PostgreSQL installed)")
    
    choice = input("Select an option (1-3): ").strip()
    
    if choice == '1':
        print_header("Neon PostgreSQL Setup")
        print("To use Neon.tech PostgreSQL:")
        print("1. Sign up for a free account at https://neon.tech")
        print("2. Create a new project")
        print("3. On your project dashboard, find and copy the connection string\n")
        
        db_url = input("Paste your Neon connection string here: ").strip()
        
        if not db_url.startswith("postgresql://"):
            print_error("Invalid connection string. It should start with 'postgresql://'")
            return False
        
        # Update .env file with connection string
        update_env_var("DATABASE_URL", db_url)
        print_success("Neon PostgreSQL configured")
        return True
    
    elif choice == '2':
        print_header("SQLite Setup")
        
        # Create a SQLite database URL
        db_path = os.path.abspath("instance/fintelligence.db")
        db_url = f"sqlite:///{db_path}"
        
        # Update .env file
        update_env_var("DATABASE_URL", db_url)
        print_success("SQLite database configured")
        return True
    
    elif choice == '3':
        print_header("Local PostgreSQL Setup")
        
        # Get PostgreSQL connection details
        host = input("PostgreSQL host (default: localhost): ").strip() or "localhost"
        port = input("PostgreSQL port (default: 5432): ").strip() or "5432"
        database = input("Database name (default: fintelligence): ").strip() or "fintelligence"
        user = input("Database user: ").strip()
        password = input("Database password: ").strip()
        
        if not user or not password:
            print_error("User and password are required")
            return False
        
        # Build connection string
        db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
        # Update .env file
        update_env_var("DATABASE_URL", db_url)
        print_success("Local PostgreSQL configured")
        return True
    
    else:
        print_error("Invalid choice")
        return False

def setup_api_key():
    """Setup Gemini API key"""
    print_header("Setting Up Gemini API Key")
    
    print("To get a Gemini API key:")
    print("1. Go to https://aistudio.google.com/app/apikey")
    print("2. Create a new API key or use an existing one\n")
    
    api_key = input("Enter your Gemini API key: ").strip()
    
    if not api_key:
        print_error("API key cannot be empty")
        return False
    
    # Update .env file
    update_env_var("GEMINI_API_KEY", api_key)
    print_success("Gemini API key configured")
    return True

def generate_secret_key():
    """Generate a random secret key for Flask"""
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(24))

def setup_env_file():
    """Create or update .env file"""
    print_header("Setting Up Environment Variables")
    
    env_path = ".env"
    env_exists = os.path.exists(env_path)
    
    if env_exists:
        print_success(".env file already exists")
    else:
        # Create a new .env file with template values
        with open(env_path, 'w') as f:
            f.write("# Fintelligence environment variables\n")
            f.write("DATABASE_URL=\n")
            f.write("GEMINI_API_KEY=\n")
            f.write(f"SECRET_KEY={generate_secret_key()}\n")
        print_success("Created .env file template")
    
    return True

def update_env_var(key, value):
    """Update a specific environment variable in .env file"""
    env_path = ".env"
    
    if os.path.exists(env_path):
        # Read existing content
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Look for existing key
        key_exists = False
        new_lines = []
        for line in lines:
            if line.strip() and line.split('=')[0].strip() == key:
                new_lines.append(f"{key}={value}\n")
                key_exists = True
            else:
                new_lines.append(line)
        
        # Add key if it doesn't exist
        if not key_exists:
            new_lines.append(f"{key}={value}\n")
        
        # Write updated content
        with open(env_path, 'w') as f:
            f.writelines(new_lines)
    else:
        # Create new .env file
        with open(env_path, 'w') as f:
            f.write(f"{key}={value}\n")

def validate_setup():
    """Validate the setup by running a check"""
    print_header("Validating Setup")
    
    # Install python-dotenv if needed
    try:
        import dotenv
    except ImportError:
        print_warning("Installing python-dotenv package...")
        run_command(f"{sys.executable} -m pip install python-dotenv")
    
    # Run the check_env.py script if it exists
    if os.path.exists("check_env.py"):
        print("Running environment variable check...")
        run_command(f"{sys.executable} check_env.py")
    
    # Check if database URL is set
    from dotenv import load_dotenv
    load_dotenv()
    
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        print_success("Database URL is configured")
    else:
        print_error("Database URL is not set")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        print_success("Gemini API key is configured")
    else:
        print_error("Gemini API key is not set")
    
    return True

def create_database_tables():
    """Create database tables"""
    print_header("Creating Database Tables")
    
    print("Attempting to create database tables...")
    result = run_command(
        f"{sys.executable} -c \"from app import app, db; app.app_context().push(); db.create_all()\"",
        "Failed to create database tables."
    )
    
    if result:
        print_success("Database tables created successfully")
    
    return result

def main():
    """Main setup function"""
    print(f"{BOLD}{BLUE}Fintelligence Setup for Windows{RESET}")
    print(f"{BOLD}{BLUE}=============================={RESET}")
    print("This script will guide you through setting up Fintelligence on your Windows system.\n")
    
    try:
        # Setup env file first (so we can update it)
        if not setup_env_file():
            return
        
        # Setup core components
        if not install_python_dependencies():
            return
        
        if not setup_directories():
            return
        
        if not setup_database():
            return
        
        if not setup_api_key():
            return
        
        # Generate secret key if it doesn't exist
        if not os.environ.get("SECRET_KEY"):
            update_env_var("SECRET_KEY", generate_secret_key())
            print_success("Generated random secret key")
        
        # Validate the setup
        validate_setup()
        
        # Create database tables
        if not create_database_tables():
            return
        
        # Final success message
        print_header("Setup Complete")
        print_success("Fintelligence has been successfully set up on your system!")
        print("\nTo run the application:")
        print("1. Open Command Prompt or PowerShell")
        print("2. Navigate to the Fintelligence directory")
        print(f"3. Run: {sys.executable} run_locally.py")
        
        # Ask if user wants to run the app now
        if input("\nDo you want to run the application now? (y/n): ").lower() == 'y':
            print_header("Starting Fintelligence")
            run_command(f"{sys.executable} run_locally.py")
    
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user.")
    except Exception as e:
        print_error(f"An unexpected error occurred: {e}")
        print("Please try running the setup again or check the error message above.")

if __name__ == "__main__":
    main()