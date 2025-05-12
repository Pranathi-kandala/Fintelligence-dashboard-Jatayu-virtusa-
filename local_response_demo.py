"""
Demo script to show how the local response mode works
"""
import os
import sys

def demo_local_chatbot():
    """Demonstrate how the local chatbot responses work"""
    # Sample financial questions to demonstrate
    sample_questions = [
        "What is a balance sheet?",
        "How do I improve my profit margins?",
        "Explain cash flow to me",
        "What are the important financial ratios?",
        "How should I manage my business debt?",
        "What are some good budgeting strategies?",
        "How can I minimize my business taxes?",
        "What is the difference between assets and liabilities?"
    ]
    
    print("Local Chatbot Response Demo")
    print("===========================")
    print("This script demonstrates the local responses that the chatbot")
    print("can provide even when the Gemini API is unavailable or quota-limited.")
    print()
    
    # Load the get_local_response function from ai_processor.py
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from ai_processor import get_local_response
        
        print("✓ Successfully loaded the local response function")
        print("\nHere are some example responses to financial questions:\n")
        
        for i, question in enumerate(sample_questions, 1):
            print(f"Question {i}: {question}")
            print("-" * 80)
            response = get_local_response(question)
            print(response)
            print("=" * 80)
            print()
            
        print("You can now use this local mode in your actual application.")
        print("Even when the Gemini API is unavailable due to quota limits,")
        print("the chatbot will still provide these helpful responses.")
        
    except ImportError:
        print("❌ Could not import get_local_response from ai_processor")
        print("Please run fix_chatbot.py first to add this functionality")
        
    except Exception as e:
        print(f"❌ Error in demo: {str(e)}")

if __name__ == "__main__":
    demo_local_chatbot()