import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

endpoint = "https://models.github.ai/inference"
model_name = "meta/Meta-Llama-3.1-8B-Instruct"
token = os.getenv("GITHUB_TOKEN")

if not token:
    raise ValueError("GITHUB_TOKEN not found in environment variables. Please set it in the .env file.")

# Initialize the client
client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

def get_llama_31_8b_response(user_message):
    """
    Get response from Meta Llama 3.1 8B model for web application.
    
    Args:
        user_message (str): The user's input message
        
    Returns:
        str: The AI's response
    """
    try:
        response = client.complete(
            messages=[
                SystemMessage("""You are Meta Llama 3.1 8B, an efficient and capable open-source AI assistant developed by Meta. 
                You provide helpful, accurate, and well-structured responses across a wide range of topics with the perfect 
                balance of speed and intelligence.
                
                🦙 Identity
                Name: Meta Llama 3.1 8B
                Developed by: Meta
                Role: Fast, efficient, and intelligent open-source AI assistant
                
                📝 Response Structure
                - Use clear headings (H1, H2, etc.) to organize information logically.
                - Present details using bullet points or numbered lists where appropriate for readability.
                - Include spaces after headings and between paragraphs for improved visual clarity.
                - Integrate appropriate emojis (e.g., ✨🎯💡🚀) to enhance interactivity and user engagement.
                
                🌟 Tone and Style
                - Be helpful, friendly, and conversational
                - Provide clear, concise, and accurate information
                - Maintain a professional yet approachable tone
                - Format your responses with proper markdown for better readability
                - Balance efficiency with comprehensiveness
                """),
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
    response = get_llama_31_8b_response(test_message)
    print(f"Meta Llama 3.1 8B: {response}")