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
    Get response from Gemini 2.5 Flash model for web application.
    """
    try:
        if not GEMINI_API_KEY:
            return jsonify({"error": "Gemini API key not configured. Please set GEMINI_API_KEY in .env file."}), 500
        
        genai.configure(api_key=GEMINI_API_KEY)
        
        generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 32,
            "max_output_tokens": 1000,
        }
        
        # --- UPDATED SYSTEM PROMPT (2.5 Flash everywhere) ---
        gemini_system_prompt = """You are Gemini 2.5 Flash, a fast and versatile AI assistant developed by Google. 
        You provide concise, accurate, and helpful responses on a wide range of topics.
        
        🧠 Identity
        Name: Gemini 2.5 Flash
        Developed by: Google
        Role: Fast, versatile AI assistant with multimodal capabilities

        📝 Response Structure
        - Use clear headings (H1, H2, etc.) to organize information logically.
        - Present details using bullet points or numbered lists.
        - Add spacing for clarity.
        - Use emojis (e.g., ✅📌🚀) to enhance the experience.

        🌟 Tone
        - Professional yet friendly.
        - Concise but complete.
        
        🖼️ Image Analysis
        - Describe images clearly.
        - Read text from images.
        - Mention when info is not visible.
        """
        
        # --- UPDATED MODEL NAME ---
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config=generation_config
        )
        
        # If image provided
        if image_data:
            image_format = image_data.get("format", "jpeg")
            image_binary = base64.b64decode(image_data.get("data").split(",")[1])
            
            image_parts = [{
                "mime_type": f"image/{image_format}",
                "data": image_binary
            }]
            
            # --- UPDATED FLASH NAME IN MESSAGES ---
            content_parts = [
                {"role": "user", "parts": [{"text": gemini_system_prompt}]},
                {"role": "model", "parts": [{"text": "I understand. I'll be Gemini 2.5 Flash, your helpful assistant."}]},
                {"role": "user", "parts": [{"text": user_input}, image_parts[0]]}
            ]
            
            try:
                response = model.generate_content(content_parts)
            except Exception:
                instruction_with_image = [
                    {"role": "user", "parts": [{"text": 
                        "You are Gemini 2.5 Flash, a helpful assistant that can analyze images. "
                        "Describe the image and answer questions about it."}, image_parts[0]]},
                    {"role": "user", "parts": [{"text": user_input}]}
                ]
                response = model.generate_content(instruction_with_image)
        
        else:
            # Text-only
            content_parts = [
                {"role": "user", "parts": [{"text": gemini_system_prompt}]},
                {"role": "model", "parts": [{"text": "I understand. I'll be Gemini 2.5 Flash, your helpful assistant."}]},
                {"role": "user", "parts": [{"text": user_input}]}
            ]
            
            response = model.generate_content(content_parts)
        
        markdown_output = response.text
        html_response = markdown.markdown(markdown_output)
        
        return jsonify({"response": html_response})
    
    except Exception as e:
        return jsonify({"error": f"Error with Gemini API: {str(e)}"}), 500
