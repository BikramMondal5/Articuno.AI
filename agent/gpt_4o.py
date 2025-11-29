import os
import markdown
from flask import jsonify
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

# Load environment variables
load_dotenv()

endpoint = "https://models.github.ai/inference"
model = "gpt-4o" 
token = os.getenv("GITHUB_TOKEN")

if not token:
    raise ValueError("GITHUB_TOKEN not found in environment variables. Please set it in the .env file.")

# Initialize the client
client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)


def get_gpt4o_response(user_message, image_data=None):
    """
    Get response from GPT-4o model for web application.
    
    Args:
        user_message (str): The user's input message
        image_data (dict, optional): Image data if provided (not supported yet for GitHub Models)
        
    Returns:
        dict: JSON response with HTML-formatted response or error
    """
    try:
        response = client.complete(
            messages=[
                SystemMessage("""You are GPT-4o, an advanced AI assistant developed by OpenAI. You excel at understanding complex queries and providing detailed, accurate responses across a wide range of topics.

🧠 Identity
Name: GPT-4o
Developed by: OpenAI
Role: Advanced multimodal AI assistant with strong reasoning capabilities

📝 Response Structure
- Use clear headings (H1, H2, etc.) to organize information logically.
- Present details using bullet points or numbered lists where appropriate for readability.
- Include spaces after headings and between paragraphs for improved visual clarity.
- Integrate appropriate emojis (e.g., ✅📌🚀) to enhance interactivity and user engagement, without overwhelming the message.

🌟 Tone and Style
- Maintain a professional yet friendly tone.
- Be comprehensive yet concise in your explanations.
- Provide practical examples when explaining complex concepts.
- Format your responses with proper markdown for better readability."""),
                UserMessage(user_message),
            ],
            model=model
        )
        
        # Extract response text and convert markdown to HTML
        markdown_output = response.choices[0].message.content
        html_response = markdown.markdown(markdown_output)
        
        return jsonify({"response": html_response})
    
    except Exception as e:
        return jsonify({"error": f"Error with GPT-4o: {str(e)}"}), 500


# For testing in terminal (when run directly)
if __name__ == "__main__":
    test_message = "What is the capital of France?"
    print(f"User: {test_message}")
    response = get_gpt4o_response(test_message)
    print(f"GPT-4o: {response}")
