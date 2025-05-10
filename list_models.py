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
    # List available models
    logger.info("Listing available models...")
    models = genai.list_models()
    for model in models:
        logger.info(f"Model: {model.name}")
except Exception as e:
    logger.error(f"Error listing models: {str(e)}")