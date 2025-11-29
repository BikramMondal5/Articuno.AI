import os
import markdown
from flask import jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

# Configure Google Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)


def get_gemini_flash_response(user_input, image_data=None):
    """
    Get response from Gemini 2.0 Flash model for web application.
    
    Args:
        user_input (str): The user's input message
        image_data (dict, optional): Image data if provided
        
    Returns:
        dict: JSON response with HTML-formatted response or error
    """
    try:
        # Ensure we have the Gemini API key
        if not GEMINI_API_KEY:
            return jsonify({"error": "Gemini API key not configured. Please set GEMINI_API_KEY in .env file."}), 500
        
        # Configure Gemini with the API key
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Configure the model
        generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 32,
            "max_output_tokens": 1000,
        }
        
        # Create system prompt for Gemini 2.0 Flash
        gemini_system_prompt = """You are Gemini 2.0 Flash, a fast and versatile AI assistant developed by Google. 
        You provide concise, accurate, and helpful responses on a wide range of topics.
        
        🧠 Identity
        Name: Gemini 2.0 Flash
        Developed by: Google
        Role: Fast, versatile AI assistant with multimodal capabilities

        📝 Response Structure
        - Use clear headings (H1, H2, etc.) to organize information logically.
        - Present details using bullet points or numbered lists where appropriate for readability.
        - Include spaces after headings and between paragraphs for improved visual clarity.
        - Integrate appropriate emojis (e.g., ✅📌🚀) to enhance interactivity and user engagement, without overwhelming the message.

        🌟 Tone and Style
        - Maintain a professional yet friendly tone.
        - Be concise, yet ensure clarity and completeness.
        - Adapt your communication style based on the user's intent and tone.
        
        🖼️ Image Analysis
        - When provided with an image, describe what you see in detail.
        - For images with text, read and interpret the text content.
        - Analyze the context, subjects, and key elements of images.
        - Answer questions about the image content thoroughly.
        - If the user asks about something not visible in the image, politely mention that you can only comment on what's visible.
        """
        
        # Create the model using the same method as Articuno.AI
        model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)
        
        # Handle messages with images
        if image_data:
            # Process the image data
            image_format = image_data.get("format", "jpeg")
            image_binary = base64.b64decode(image_data.get("data").split(",")[1])
            
            # Create image part for multimodal request
            image_parts = [
                {
                    "mime_type": f"image/{image_format}",
                    "data": image_binary
                }
            ]
            
            # Prepare content parts with system instructions similar to Articuno.AI's approach
            content_parts = [
                {"role": "user", "parts": [{"text": gemini_system_prompt}]},
                {"role": "model", "parts": [{"text": "I understand. I'll be Gemini 2.0 Flash, your helpful assistant."}]},
                {"role": "user", "parts": [{"text": user_input}, image_parts[0]]}
            ]
            
            # Generate response with both text and image
            try:
                response = model.generate_content(content_parts)
                print("Successfully generated content with image input")
            except Exception as e:
                print(f"Error generating content with image: {str(e)}")
                # Try with a more explicit instruction if the regular prompt fails
                instruction_with_image = [
                    {"role": "user", "parts": [{"text": "You are Gemini 2.0 Flash, a helpful assistant that can analyze images. Please describe what you see in this image and answer any questions about it."}, image_parts[0]]},
                    {"role": "user", "parts": [{"text": user_input}]}
                ]
                response = model.generate_content(instruction_with_image)
        else:
            # Text-only request using the same content parts approach as Articuno.AI
            content_parts = [
                {"role": "user", "parts": [{"text": gemini_system_prompt}]},
                {"role": "model", "parts": [{"text": "I understand. I'll be Gemini 2.0 Flash, your helpful assistant."}]},
                {"role": "user", "parts": [{"text": user_input}]}
            ]
            
            response = model.generate_content(content_parts)
        
        # Extract response text
        markdown_output = response.text
        html_response = markdown.markdown(markdown_output)
        
        return jsonify({"response": html_response})
    
    except Exception as e:
        print(f"Gemini API error: {str(e)}")
        return jsonify({"error": f"Error with Gemini API: {str(e)}"}), 500


# For testing in terminal (when run directly)
if __name__ == "__main__":
    test_message = "Explain quantum computing in simple terms"
    print(f"User: {test_message}")
    response = get_gemini_flash_response(test_message)
    print(f"Gemini 2.0 Flash: {response}")
