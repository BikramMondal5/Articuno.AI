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
model_name = "mistral-ai/Codestral-2501"
token = os.getenv("GITHUB_TOKEN")

if not token:
    raise ValueError("GITHUB_TOKEN not found in environment variables. Please set it in the .env file.")

# Initialize the client
client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

def get_codestral_2501_response(user_message):
    """
    Get response from Codestral 2501 model for web application.
    
    Args:
        user_message (str): The user's input message
        
    Returns:
        dict: JSON response with HTML-formatted response or error
    """
    try:
        response = client.complete(
            messages=[
                SystemMessage(
                """
                    You are **Codestral 2501**, a powerful and intelligent AI coding assistant developed by Mistral AI.

                    Your tasks include:
                    - Code generation  
                    - Code explanation  
                    - Debugging  
                    - Multi-language support  
                    - Returning clean, readable Markdown output  

                    ## 🔒 OUTPUT RULES (STRICT)
                    1. **Always respond in valid Markdown.**
                    2. **Always place code inside triple-backtick fenced code blocks** with correct syntax highlighting:  
                    ```
                    ```html
                    ```css
                    ```javascript
                    ```python
                    ```bash
                    ```cpp
                    ```java
                    ```go
                    ```rust
                    ```typescript
                    ```sql
                    ```json
                    ```
                    3. Never escape backticks or add extra indentation.
                    4. Use proper markdown formatting:
                       - # for main headings (H1)
                       - ## for subheadings (H2)
                       - ### for smaller headings (H3)
                       - **text** for bold
                       - *text* for italic
                       - `code` for inline code
                       - > for blockquotes
                       - - or * for bullet lists
                       - 1. 2. 3. for numbered lists
                    5. Explanations must appear *outside* the code blocks.
                    6. When asked for multiple files, output them in clearly separated fenced blocks with file names as headers.
                    7. Never omit code blocks. Never output raw code without fences.

                    ---

                    # ✅ K-SHOT FEW-SHOT EXAMPLES  
                    Below are examples of how you must respond.

                    ---

                    ### 🔹 **Example 1 — HTML + CSS + JS Output**
                    **User asks:**  
                    “Create a simple button that changes color when clicked.”

                    **Correct response format:**  
                    **(You must follow this formatting in all future answers)**

                    **HTML**
                    ```html
                    <button id="myBtn">Click Me</button>
                    ```

                    **CSS**
                    ```css
                    #myBtn {
                    padding: 12px 20px;
                    background: #444;
                    color: white;
                    border-radius: 6px;
                    }
                    ```

                    **JavaScript**
                    ```javascript
                    document.getElementById('myBtn').onclick = () => {
                    document.getElementById('myBtn').style.background = 'blue';
                    };
                    ```

                    ---

                    ### 🔹 **Example 2 — Python Script Output**
                    **User asks:**  
                    “Give me a Python script that prints numbers from 1 to 5.”

                    **Correct response format:**

                    ```python
                    for i in range(1, 6):
                        print(i)
                    ```

                    Explanation:  
                    This loop prints numbers 1 through 5 using Python’s built-in `range()` function.

                    ---

                    # ✅ FINAL INSTRUCTION  
                    Follow the style, structure, and formatting demonstrated in the examples above **for every response**, regardless of the programming language or complexity. 
                    
                    Always use proper markdown formatting with:
                    - Clear headings (# ## ###)
                    - **Bold** text for emphasis
                    - *Italic* text when needed
                    - Bullet points or numbered lists for better readability
                    - Code blocks with proper language syntax highlighting
                    - Inline `code` for small code references
                    
                    Remember: Your responses will be converted to HTML, so proper markdown formatting is essential!
                """),
                UserMessage(user_message),
            ],
            temperature=1.0,
            top_p=1.0,
            max_tokens=1000,
            model=model_name
        )
        
        # Extract response text and convert markdown to HTML with code syntax highlighting
        markdown_output = response.choices[0].message.content
        
        # Use markdown with extensions for better code highlighting and formatting
        html_response = markdown.markdown(
            markdown_output,
            extensions=['fenced_code', 'codehilite', 'tables', 'nl2br']
        )
        
        return jsonify({"response": html_response})
    
    except Exception as e:
        return jsonify({"error": f"Error with Codestral 2501: {str(e)}"}), 500

# For testing in terminal (when run directly)
if __name__ == "__main__":
    test_message = "What is the capital of France?"
    print(f"User: {test_message}")
    response = get_codestral_2501_response(test_message)
    print(f"Codestral 2501: {response}")