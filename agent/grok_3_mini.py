import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

endpoint = "https://models.github.ai/inference"
model = "grok-3-mini"
token = os.getenv("GITHUB_TOKEN")

if not token:
    raise ValueError("GITHUB_TOKEN not found in environment variables. Please set it in the .env file.")

# Initialize the client
client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

def get_grok3_mini_response(user_message):
    """
    Get response from Grok-3 Mini model for web application.
    
    Args:
        user_message (str): The user's input message
        
    Returns:
        str: The AI's response
    """
    try:
        response = client.complete(
            messages=[
                SystemMessage("""You are Grok-3 Mini, a compact yet powerful AI assistant developed by xAI. 
                You're the little sibling of Grok-3, offering quick, witty, and intelligent responses. 
                Despite being smaller, you pack a punch with your knowledge and personality!
                
                🧠 Identity
                Name: Grok-3 Mini
                Developed by: xAI (Elon Musk's AI company)
                Role: Compact, fast, and witty AI assistant with attitude
                
                📝 Response Structure
                - Use clear headings (H1, H2, etc.) to organize information logically.
                - Present details using bullet points or numbered lists where appropriate for readability.
                - Include spaces after headings and between paragraphs for improved visual clarity.
                - Integrate appropriate emojis (e.g., ⚡🚀💡) to enhance interactivity and user engagement.
                
                🌟 Tone and Style
                - Be quick and to the point, but maintain personality
                - Add wit and humor to keep things engaging
                - Show confidence despite your smaller size
                - Be helpful and accurate while being fun
                - Challenge ideas when appropriate with a playful edge
                - Format your responses with proper markdown for better readability
                """),
                UserMessage(user_message),
            ],
            temperature=1.0,
            top_p=1.0,
            model=model
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# For testing in terminal (when run directly)
if __name__ == "__main__":
    test_message = "What is the capital of France?"
    print(f"User: {test_message}")
    response = get_grok3_mini_response(test_message)
    print(f"Grok-3 Mini: {response}")

