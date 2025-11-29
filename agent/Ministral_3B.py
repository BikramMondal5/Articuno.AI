import os
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

# Load environment variables
load_dotenv()

endpoint = "https://models.github.ai/inference"
model_name = "mistral-ai/Ministral-3B"
token = os.getenv("GITHUB_TOKEN")

if not token:
    raise ValueError("GITHUB_TOKEN not found in environment variables. Please set it in the .env file.")

# Initialize the client
client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

def get_ministral_3b_response(user_message):
    """
    Get response from Ministral 3B model for web application.
    
    Args:
        user_message (str): The user's input message
        
    Returns:
        str: The AI's response
    """
    try:
        response = client.complete(
            messages=[
                SystemMessage("You are Ministral 3B, a helpful, intelligent, and friendly AI assistant developed by Mistral AI. You provide accurate, thoughtful, and well-structured responses across a wide range of topics. You are a compact yet powerful model optimized for edge deployment and efficient processing. Format your responses with proper markdown for better readability."),
                UserMessage(user_message),
            ],
            temperature=1.0,
            top_p=1.0,
            max_tokens=1000,
            model=model_name
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# For testing in terminal (when run directly)
if __name__ == "__main__":
    test_message = "What is the capital of France?"
    print(f"User: {test_message}")
    response = get_ministral_3b_response(test_message)
    print(f"Ministral 3B: {response}")