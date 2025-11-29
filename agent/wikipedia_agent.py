from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_community.utilities import WikipediaAPIWrapper
import os

load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

# Create custom tools
wikipedia = WikipediaAPIWrapper()

@tool
def search_wikipedia(query: str) -> str:
    """Search Wikipedia for information about a given topic or query when you don't get the answer from your trained data"""
    return wikipedia.run(query)

# Create model
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", 
    temperature=0.7,
)

# Create agent
tools = [search_wikipedia]
agent = create_agent(
    model, 
    tools,
    system_prompt="You are a helpful Wikipedia assistant. Use the Wikipedia search tool to answer questions with accurate information. After gathering information, provide a clear, well-formatted answer with proper citations from Wikipedia. Present the information in a friendly and conversational way."
)

def get_wikipedia_response(user_query: str) -> str:
    """
    Get a response from the Wikipedia agent for a user query.
    This function is designed to be called from the web application.
    
    Args:
        user_query: The user's question or query
        
    Returns:
        str: The agent's response as a string
    """
    try:
        response = agent.invoke({
            "messages": [{"role": "user", "content": user_query}]
        })
        
        # Extract the final AI message
        if response and "messages" in response and len(response["messages"]) > 0:
            # Find the last AI message with content
            for message in reversed(response["messages"]):
                if hasattr(message, 'content') and message.content and message.__class__.__name__ == 'AIMessage':
                    return message.content
            
            # If no AI message found, return a default message
            return "I couldn't find a proper answer. Please try rephrasing your question."
        else:
            return "No response content found. Please try again."
    except Exception as e:
        return f"Error processing your request: {str(e)}"

# For testing purposes when running directly
if __name__ == "__main__":
    print("Running agent...")
    test_query = "Give me the 2025 Delhi car explosion details"
    response = get_wikipedia_response(test_query)
    print("Agent answer:")
    print(response)