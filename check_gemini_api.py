"""
Script to verify that the Gemini API key is working correctly
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check if GEMINI_API_KEY is in environment
gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
if not gemini_api_key:
    print("❌ GEMINI_API_KEY not found in environment variables.")
    print("Please add it to your .env file or set it as an environment variable.")
    sys.exit(1)

print(f"✓ Found Gemini API key with length: {len(gemini_api_key)}")
print(f"  First few characters: {gemini_api_key[:4]}...")
print(f"  Last few characters: ...{gemini_api_key[-4:]}")

# Try to use the Gemini API
try:
    print("\nTesting connection to Gemini API...")
    import google.generativeai as genai
    
    # Configure the API
    genai.configure(api_key=gemini_api_key)
    
    # Try a simple generation
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content("Hello, please respond with only the word 'SUCCESS' if you can receive this message.")
    
    print(f"\nAPI Response:\n{response.text}\n")
    if "SUCCESS" in response.text.upper():
        print("✓ Gemini API connection successful!")
    else:
        print("✓ Gemini API responded, but with unexpected content.")
        print("The API key is valid, but there might be other issues.")
    
except Exception as e:
    print(f"\n❌ Error connecting to Gemini API: {e}")
    print("\nPossible solutions:")
    if "quota" in str(e).lower():
        print("- Your API key has exceeded its quota limits.")
        print("- Create a new API key at https://aistudio.google.com/app/apikey")
    elif "invalid" in str(e).lower():
        print("- The API key appears to be invalid or malformed.")
        print("- Make sure you copied the entire key correctly.")
    else:
        print("- Check your internet connection.")
        print("- Make sure google-generativeai package is installed: pip install google-generativeai")
        print("- Try creating a new API key at https://aistudio.google.com/app/apikey")
    
    print("\nError details:", str(e))

print("\nAPI check complete.")