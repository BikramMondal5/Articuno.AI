import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

endpoint = "https://models.github.ai/inference"
model_name = "cohere/Cohere-command-r-plus-08-2024"
token = os.getenv("GITHUB_TOKEN")

if not token:
    raise ValueError("GITHUB_TOKEN not found in environment variables. Please set it in the .env file.")

# Initialize the client
client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

def get_cohere_command_r_plus_response(user_message):
    """
    Get response from Cohere Command R+ model for web application.
    
    Args:
        user_message (str): The user's input message
        
    Returns:
        str: The AI's response
    """
    try:
        response = client.complete(
            messages=[
                SystemMessage("You are Cohere Command R+, an advanced AI assistant developed by Cohere with enhanced reasoning capabilities. You excel at complex tasks, detailed analysis, and providing comprehensive answers. Format your responses with proper markdown for better readability. Use clear headings, bullet points, and appropriate emojis to enhance user engagement and clarity."),
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
    response = get_cohere_command_r_plus_response(test_message)
    print(f"Cohere Command R+: {response}")