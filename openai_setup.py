"""
OpenAI Integration for Fintelligence Chatbot
Uses the official OpenAI API for more reliable responses
"""

import os
import json
import logging
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('fintelligence.openai_official')

# Initialize the OpenAI client with the API key
openai_api_key = os.environ.get("OPENAI_API_KEY")
if openai_api_key:
    # Only show first 4 and last 4 characters for security
    visible_key = f"{openai_api_key[:4]}...{openai_api_key[-4:]}" if len(openai_api_key) > 8 else "****"
    logger.info(f"Using OpenAI API key: {visible_key} (length: {len(openai_api_key)})")
    client = OpenAI(api_key=openai_api_key)
    logger.info("Successfully initialized OpenAI client")
else:
    logger.warning("OPENAI_API_KEY environment variable not set")
    client = None

def get_openai_response(prompt):
    """
    Get a response from the OpenAI API using the official client
    
    Args:
        prompt (str): The prompt to send to the API
        
    Returns:
        str: The response from the API
    """
    if not client:
        logger.warning("OpenAI client not initialized. Check your API key.")
        return None
        
    try:
        # Call the OpenAI API
        logger.info(f"Sending request to OpenAI API with prompt length: {len(prompt)}")
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using 3.5 for cost efficiency, can be upgraded to gpt-4
            messages=[
                {"role": "system", "content": "You are a financial expert assistant. Provide clear, concise explanations about financial concepts and analysis. Always be accurate and helpful."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.2
        )
        
        # Extract the response text
        response_text = response.choices[0].message.content
        if response_text:
            logger.info(f"Received response from OpenAI API of length: {len(response_text)}")
        else:
            logger.warning("Received empty response from OpenAI API")
        return response_text
        
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {str(e)}")
        return None