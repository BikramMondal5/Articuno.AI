import os
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

# Load environment variables
load_dotenv()

endpoint = "https://models.github.ai/inference"
model = "gpt-4o-mini" 
token = os.getenv("GITHUB_TOKEN")

if not token:
    raise ValueError("GITHUB_TOKEN not found in environment variables. Please set it in the .env file.")

# Initialize the client
client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

def get_gpt4o_mini_response(user_message):
    """
    Get response from GPT-4o-mini model for web application.
    
    Args:
        user_message (str): The user's input message
        
    Returns:
        str: The AI's response
    """
    try:
        response = client.complete(
            messages=[
                SystemMessage("You are GPT-4o-mini, a helpful, intelligent, and friendly AI assistant developed by OpenAI. You provide accurate, thoughtful, and well-structured responses across a wide range of topics. Format your responses with proper markdown for better readability."),
                UserMessage(user_message),
            ],
            model=model
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# For testing in terminal (when run directly)
if __name__ == "__main__":
    test_message = "What is the capital of France?"
    print(f"User: {test_message}")
    response = get_gpt4o_mini_response(test_message)
    print(f"GPT-4o-mini: {response}")

