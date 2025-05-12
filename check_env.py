"""
Simple script to check if environment variables from .env are loaded properly
"""
import os
import sys
from dotenv import load_dotenv

# Try to load environment variables from .env file
print("Attempting to load .env file...")
load_dotenv()

# Check for GEMINI_API_KEY
gemini_key = os.environ.get("GEMINI_API_KEY", "")
if gemini_key:
    # Mask most of the key for security
    masked_key = f"{gemini_key[:4]}...{gemini_key[-4:]}" if len(gemini_key) > 8 else "***"
    print(f"✓ GEMINI_API_KEY found with length {len(gemini_key)} chars: {masked_key}")
else:
    print("❌ GEMINI_API_KEY not found in environment variables")
    
# Check for DATABASE_URL
db_url = os.environ.get("DATABASE_URL", "")
if db_url:
    # Mask password in the URL for security
    if ":" in db_url and "@" in db_url:
        parts = db_url.split("@")
        credentials = parts[0].split(":")
        masked_url = f"{credentials[0]}:****@{parts[1]}"
        print(f"✓ DATABASE_URL found: {masked_url}")
    else:
        print(f"✓ DATABASE_URL found but in unexpected format")
else:
    print("❌ DATABASE_URL not found in environment variables")

# Check for SECRET_KEY
secret_key = os.environ.get("SECRET_KEY", "")
if secret_key:
    print(f"✓ SECRET_KEY found with length {len(secret_key)} chars")
else:
    print("❌ SECRET_KEY not found in environment variables")

print("\nEnvironment variable check complete.")