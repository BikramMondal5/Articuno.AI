"""
Main agent logic for Bikram.AI using LangChain and RAG.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
import markdown

from .config import MODEL_NAME, TEMPERATURE, BIKRAM_SYSTEM_PROMPT
from .tools import get_all_tools

# Lazy initialization
_agent = None


def _get_agent():
    """Lazy initialization of the Bikram.AI agent."""
    global _agent
    
    if _agent is None:
        # Create model with Bikram's personality settings
        model = ChatGoogleGenerativeAI(
            model=MODEL_NAME,
            temperature=TEMPERATURE,
        )

        # Get all tools including RAG-powered resume search
        tools = get_all_tools()
        
        # Create agent using LangGraph's create_react_agent
        # Note: LangGraph uses 'state_modifier' instead of 'system_prompt'
        _agent = create_react_agent(
            model, 
            tools
        )
    
    return _agent


def get_bikram_ai_response(user_message: str) -> str:
    """
    Get response from Bikram.AI - A personalized AI assistant reflecting Bikram Mondal's personality.
    
    This version uses RAG to retrieve information from Bikram's resume instead of hard-coded details.
    
    Args:
        user_message (str): The user's input message
        
    Returns:
        str: The AI's response in Bikram's friendly and helpful style, with markdown converted to HTML
    """
    try:
        agent = _get_agent()
        
        # Prepend system prompt to the user message for LangGraph
        full_message = f"{BIKRAM_SYSTEM_PROMPT}\n\nUser: {user_message}"
        
        response = agent.invoke({
            "messages": [{"role": "user", "content": full_message}]
        })
        
        # Extract the final AI message from LangGraph response
        markdown_output = None
        if response and "messages" in response and len(response["messages"]) > 0:
            # Find the last AI message with content
            for message in reversed(response["messages"]):
                if hasattr(message, 'content') and message.content:
                    # Check if it's an AI message (not human)
                    if hasattr(message, 'type') and message.type == 'ai':
                        # Handle content that might be a list or string
                        content = message.content
                        if isinstance(content, list):
                            # If it's a list, join the text parts
                            markdown_output = ' '.join(str(item.get('text', item)) if isinstance(item, dict) else str(item) for item in content)
                        else:
                            markdown_output = str(content)
                        break
                    # Fallback: check class name
                    elif message.__class__.__name__ == 'AIMessage':
                        # Handle content that might be a list or string
                        content = message.content
                        if isinstance(content, list):
                            # If it's a list, join the text parts
                            markdown_output = ' '.join(str(item.get('text', item)) if isinstance(item, dict) else str(item) for item in content)
                        else:
                            markdown_output = str(content)
                        break
            
            if not markdown_output:
                markdown_output = "I couldn't process that request properly. Please try rephrasing your question!"
        else:
            markdown_output = "No response content found. Please try again."
        
        # Convert markdown to HTML with code syntax highlighting
        html_response = markdown.markdown(
            markdown_output,
            extensions=[
                'fenced_code',
                'codehilite',
                'tables',
                'nl2br'
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'linenums': False,
                    'guess_lang': True,
                    'noclasses': False
                }
            }
        )
        
        return html_response
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in get_bikram_ai_response: {error_details}")
        return f"Error: {str(e)}"

