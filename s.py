import google.generativeai as genai
import os

def call_gemini_2_0_flash(prompt: str) -> str:
    """
    Calls the Gemini 2.0 Flash model with the given prompt.

    Args:
        prompt: The text prompt to send to the model.

    Returns:
        The generated text response from the model.
    """
    # Ensure your Google API key is set as an environment variable
    # e.g., export GOOGLE_API_KEY='YOUR_API_KEY'
    api_key = "AIzaSyBOmXG6FF41CHR7iLfolgH9ZCndrRqAYxg"
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set.")

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)

    return response.text

if __name__ == '__main__':
    # Example usage:
    # Make sure to set your GOOGLE_API_KEY environment variable
    # export GOOGLE_API_KEY='YOUR_API_KEY'
    try:
        user_prompt = "What is the capital of France?"
        gemini_response = call_gemini_2_0_flash(user_prompt)
        print(f"Prompt: {user_prompt}")
        print(f"Gemini 2.0 Flash Response: {gemini_response}")

        user_prompt_2 = "Write a short poem about a cat."
        gemini_response_2 = call_gemini_2_0_flash(user_prompt_2)
        print(f"\nPrompt: {user_prompt_2}")
        print(f"Gemini 2.0 Flash Response: {gemini_response_2}")

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
