"""
OpenAI Financial Processor
Alternative API for financial question answering
"""

import os
import json
import logging
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('fintelligence.openai')

class OpenAIProcessor:
    """
    Class to handle OpenAI API calls as an alternative to Gemini
    This uses the free public Replit AI API endpoint, which doesn't require payment
    """
    
    def __init__(self):
        """Initialize the OpenAI processor"""
        self.api_url = "https://replit.com/.openai/v1/chat/completions"
        self.model = "gpt-3.5-turbo"  # Default model available in Replit
        logger.info(f"Initialized OpenAI processor with model: {self.model}")
        
    def get_response(self, prompt):
        """
        Get a response from the OpenAI API
        
        Args:
            prompt (str): The prompt to send to the API
            
        Returns:
            str: The response from the API
        """
        try:
            # Prepare the request
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a financial expert assistant. Provide clear, concise explanations about financial concepts and analysis. Always be accurate and helpful."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.2
            }
            
            # Make the request
            logger.info(f"Sending request to OpenAI API with prompt length: {len(prompt)}")
            response = requests.post(self.api_url, headers=headers, json=data)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the response
                response_data = response.json()
                
                # Extract the response text
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    return response_data['choices'][0]['message']['content']
                else:
                    logger.error(f"No choices in response: {response_data}")
                    return "I'm sorry, but I couldn't generate a response at this time."
            else:
                logger.error(f"Error calling OpenAI API: {response.status_code} - {response.text}")
                return f"I encountered an error processing your question. Please try again later."
                
        except Exception as e:
            logger.error(f"Exception when calling OpenAI API: {str(e)}")
            return f"I'm sorry, but I encountered a technical issue. Please try again later."
            
# Create an instance of the OpenAI processor
openai_processor = OpenAIProcessor()

def get_openai_response(prompt):
    """
    Get a response from the OpenAI API
    
    Args:
        prompt (str): The prompt to send to the API
        
    Returns:
        str: The response from the API
    """
    return openai_processor.get_response(prompt)