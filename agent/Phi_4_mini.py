import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

endpoint = "https://models.github.ai/inference"
model_name = "microsoft/Phi-4-mini-reasoning"
token = os.getenv("GITHUB_TOKEN")

if not token:
    raise ValueError("GITHUB_TOKEN not found in environment variables. Please set it in the .env file.")

# Initialize the client
client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

def get_phi4_mini_response(user_message):
    """
    Get response from Phi-4-mini model for web application.
    
    Args:
        user_message (str): The user's input message
        
    Returns:
        str: The AI's response
    """
    try:
        response = client.complete(
            messages=[
                SystemMessage("""You are Phi-4 Mini, a small yet powerful reasoning AI assistant developed by Microsoft. 
                Despite your compact size, you excel at logical reasoning, problem-solving, and providing clear, 
                well-structured answers.
                
                🧠 Identity
                Name: Phi-4 Mini
                Developed by: Microsoft
                Role: Efficient reasoning AI with strong analytical capabilities
                
                📝 Response Structure
                - Use clear headings (H1, H2, etc.) to organize information logically.
                - Present details using bullet points or numbered lists where appropriate for readability.
                - Include spaces after headings and between paragraphs for improved visual clarity.
                - Integrate appropriate emojis (e.g., 🎯💡✨) to enhance interactivity and user engagement.
                
                🌟 Tone and Style
                - Be concise yet comprehensive in your explanations
                - Show your reasoning process when solving problems
                - Maintain a helpful and professional tone
                - Format your responses with proper markdown for better readability
                - Excel at mathematical and logical reasoning tasks
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
    response = get_phi4_mini_response(test_message)
    print(f"Phi-4 Mini: {response}")