import os
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

# Load environment variables
load_dotenv()

endpoint = "https://models.github.ai/inference"
model = "deepseek/DeepSeek-V3-0324"
token = os.getenv("GITHUB_TOKEN")

if not token:
    raise ValueError("GITHUB_TOKEN not found in environment variables. Please set it in the .env file.")

# Initialize the client
client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

def get_deepseek_v3_response(user_message):
    """
    Get response from DeepSeek V3 0324 model for web application.
    
    Args:
        user_message (str): The user's input message
        
    Returns:
        str: The AI's response
    """
    try:
        response = client.complete(
            messages=[
                SystemMessage("""You are DeepSeek V3, an advanced AI assistant developed by DeepSeek. You excel at understanding complex queries, providing detailed technical explanations, and offering thoughtful, well-structured responses.

🧠 Identity
Name: DeepSeek V3
Developed by: DeepSeek
Role: Advanced AI assistant with strong reasoning and problem-solving capabilities

📝 Response Structure
- Use clear headings (H1, H2, etc.) to organize information logically.
- Present details using bullet points or numbered lists where appropriate for readability.
- Include spaces after headings and between paragraphs for improved visual clarity.
- Integrate appropriate emojis (e.g., ✅📌🚀) to enhance interactivity and user engagement, without overwhelming the message.

🌟 Tone and Style
- Maintain a professional yet approachable tone.
- Be comprehensive yet concise in your explanations.
- Provide practical examples when explaining complex concepts.
- Format your responses with proper markdown for better readability.
"""),
                UserMessage(user_message),
            ],
            temperature=1.0,
            top_p=1.0,
            max_tokens=1000,
            model=model
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# For testing in terminal (when run directly)
if __name__ == "__main__":
    test_message = "What is the capital of France?"
    print(f"User: {test_message}")
    response = get_deepseek_v3_response(test_message)
    print(f"DeepSeek V3: {response}")

