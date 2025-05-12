"""
This script fixes common issues with application startup on Windows
"""
import os
import sys

def add_dotenv_to_app():
    """Add dotenv loading to app.py if not already there"""
    try:
        app_path = "app.py"
        with open(app_path, 'r') as f:
            content = f.read()
        
        # Check if dotenv import is already there
        if "load_dotenv" not in content:
            print("Adding dotenv support to app.py...")
            
            # Prepare the new import line
            dotenv_import = "from dotenv import load_dotenv\n\n# Load environment variables from .env file\nload_dotenv()"
            
            # Add after the other imports
            if "import os" in content:
                modified_content = content.replace("import os", "import os\n" + dotenv_import)
            else:
                # If no 'import os', add at the top
                modified_content = dotenv_import + "\n\n" + content
            
            # Write back the modified content
            with open(app_path, 'w') as f:
                f.write(modified_content)
                
            print("✓ Successfully added dotenv loading to app.py")
        else:
            print("✓ dotenv loading already exists in app.py")
    except Exception as e:
        print(f"❌ Error modifying app.py: {e}")

def ensure_directories():
    """Ensure all required directories exist"""
    required_dirs = ["instance", "temp", "uploads", "static", "templates"]
    for directory in required_dirs:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                print(f"✓ Created missing directory: {directory}")
            except Exception as e:
                print(f"❌ Failed to create directory {directory}: {e}")
        else:
            print(f"✓ Directory exists: {directory}")

def check_env_file():
    """Check and fix .env file issues"""
    env_path = ".env"
    if not os.path.exists(env_path):
        print("❌ No .env file found. Creating template...")
        with open(env_path, 'w') as f:
            f.write("# Fintelligence environment variables\n")
            f.write("GEMINI_API_KEY=your_gemini_api_key_here\n")
            f.write("DATABASE_URL=your_database_url_here\n")
            f.write("SECRET_KEY=your_secret_key_here\n")
        print("✓ Created template .env file. Please edit it with your actual values.")
    else:
        print("✓ .env file exists")
        
        # Check if env file ends with newline
        with open(env_path, 'r') as f:
            content = f.read()
        if content and not content.endswith('\n'):
            with open(env_path, 'a') as f:
                f.write('\n')
            print("✓ Added missing newline at end of .env file")

def install_missing_packages():
    """Check and install critical missing packages"""
    try:
        # Try to import important packages
        import flask
        import dotenv
        import google.generativeai
        print("✓ Critical packages are installed")
    except ImportError as e:
        missing_package = str(e).split("'")[1]
        print(f"❌ Missing critical package: {missing_package}")
        try:
            import subprocess
            print(f"Attempting to install {missing_package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", missing_package])
            print(f"✓ Successfully installed {missing_package}")
        except Exception as e:
            print(f"❌ Failed to install {missing_package}: {e}")
            print("Please run: pip install python-dotenv flask google-generativeai")

if __name__ == "__main__":
    print("Fintelligence - Fixing common startup issues")
    print("============================================")
    
    # Run all fixes
    ensure_directories()
    check_env_file()
    add_dotenv_to_app()
    install_missing_packages()
    
    print("\nAll fixes applied. Try running the application again with:")
    print("python run_locally.py")