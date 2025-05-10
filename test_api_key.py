import os
import google.generativeai as genai
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('api_test')

# Get the API key from environment
gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
if not gemini_api_key:
    logger.error("GEMINI_API_KEY environment variable not set")
    exit(1)

logger.info(f"Testing API key: {gemini_api_key[:4]}...{gemini_api_key[-4:]} (length: {len(gemini_api_key)})")

# Configure the API
genai.configure(api_key=gemini_api_key)

try:
    # Try with the flash model which has higher rate limits
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    response = model.generate_content("Hello, please respond with the text 'API key is working' if you can see this message.")
    print("API Response:", response.text)
    logger.info("API key test successful!")
except Exception as e:
    logger.error(f"API key test failed: {str(e)}")