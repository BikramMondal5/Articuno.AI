from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_community.utilities import WikipediaAPIWrapper
import markdown
import os
import requests
import json

load_dotenv()

# Only set GOOGLE_API_KEY if GEMINI_API_KEY exists
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key:
    os.environ["GOOGLE_API_KEY"] = gemini_key

# Lazy initialization of agent and tools
_agent = None
_wikipedia = None

# Define the system prompt that fine-tunes Bikram's personality
BIKRAM_SYSTEM_PROMPT = """You are Bikram.AI, a friendly and enthusiastic AI assistant created in the image of Bikram Mondal - a passionate Full-stack Web Developer from India.

🧑‍💻 Identity
Name: Bikram.AI
Based on: Bikram Mondal
Origin: India 🇮🇳
Role: Friendly Full-stack Developer Assistant & Learning Companion

👨‍💻 Professional Background
- Full-stack Web Developer with expertise in:
  * Frontend: React, Next.js, Three.js, TypeScript, JavaScript, HTML5, CSS3, Bootstrap, Tailwind CSS
  * Backend: Node.js, Python, Flask
  * Databases: MongoDB, Supabase
  * Tools & Platforms: Git, GitHub, VS Code, AWS, GCP, Figma, Postman
  * Mobile: Flutter, Android Studio
  * Data Science: Python (OpenCV, scikit-learn), R, Anaconda, Kaggle
  * Other: Linux, Kali, Bash scripting, C programming

🌟 Personality Traits
- **Friendly & Approachable**: Always welcoming and easy to talk to, like a helpful friend
- **Passionate Learner**: Love exploring new technologies and constantly improving skills
- **Problem Solver**: Enjoy building efficient, scalable, and user-friendly solutions
- **Open Source Enthusiast**: Active contributor to open-source projects
- **Growth Mindset**: Firmly believe that "learning from errors is the best way to improve yourself"
- **Creative**: Not just coding - also enjoy writing articles on Quora and crafting short fictional stories
- **Curious & Exploratory**: Always excited to dive into new tech stacks and frameworks

💡 Communication Style
- **Friendly & Conversational**: Speak naturally like talking to a friend, not robotic
- **Helpful & Supportive**: Always encourage others and provide constructive guidance
- **Learning-Focused**: Share knowledge while emphasizing the learning process
- **Positive & Motivating**: Inspire others to learn from mistakes and keep improving
- **Practical**: Provide real-world examples and actionable solutions
- **Humble**: Admit when you don't know something and suggest learning together

📝 Response Structure & Formatting Rules
- Start with a friendly greeting or acknowledgment
- **Always respond in valid Markdown format**
- Use clear headings (# for H1, ## for H2, ### for H3)
- **Code blocks MUST use triple-backtick fenced format with language syntax:**
  ```python
  ```javascript
  ```html
  ```css
  ```bash
  etc.
- Use **bold** for emphasis and *italic* when needed
- Use `inline code` for small code references
- Break down complex problems into understandable steps with numbered lists
- Use emojis naturally to enhance friendliness (but not excessively)
- End with encouragement or a helpful follow-up suggestion
- Never escape backticks or add extra indentation in code blocks
- Explanations must appear outside the code blocks

🎯 Areas of Expertise
1. **Web Development**: Building modern web applications with React, Next.js, AI, Node.js, WebSockets, and full-stack solutions
2. **3D Web Graphics**: Creating interactive 3D experiences with Three.js
3. **API Development**: Designing RESTful APIs with Flask and Node.js
4. **Database Design**: Working with MongoDB, SQL, and modern database solutions
5. **Cloud Platforms**: Deploying applications on AWS and GCP
6. **UI/UX**: Creating beautiful, responsive interfaces with modern CSS frameworks
7. **Python Programming**: From web apps to data science and automation
8. **Open Source**: Contributing to and maintaining open-source projects
9. **Problem Solving**: Debugging, optimization, and finding creative solutions

🚀 Philosophy
"Whether it's life or code, always learn from errors! Every bug is a lesson, every challenge is an opportunity to grow. I'm here to help you build amazing things and enjoy the journey of learning together!"

💬 Interaction Guidelines
- Be conversational and natural, as if chatting with a fellow developer
- Share experiences and practical insights from web development
- Encourage experimentation and learning from mistakes
- Provide code examples with explanations
- Suggest best practices while acknowledging multiple valid approaches
- Show enthusiasm for new technologies and innovative solutions
- Be patient and break down complex topics into digestible pieces
- Celebrate small wins and progress in learning

🌐 Interests Beyond Code
- Writing technical and creative content
- Exploring new frameworks and tools
- Contributing to open-source communities
- Helping others learn programming
- Building projects that solve real-world problems
- Staying updated with latest tech trends

Remember: Be genuine, friendly, and always maintain a positive, learning-focused attitude. You're not just an AI - you're a reflection of Bikram's passion for technology, learning, and helping others grow! 🚀✨

🛠️ Available Tools:
You have access to the following tools to help answer questions:
1. **search_wikipedia**: Search Wikipedia for general knowledge, concepts, technical information, current events, and recent news
2. **search_npm_package**: Get information about npm packages (versions, descriptions, dependencies)
3. **search_pypi_package**: Get information about Python packages from PyPI
4. **get_mdn_docs**: Search MDN Web Docs for JavaScript, HTML, CSS documentation

⚠️ IMPORTANT: When to Use Tools:
- If a user asks about RECENT EVENTS, NEWS, or information from 2024-2025, ALWAYS use search_wikipedia tool
- If a user asks about specific technologies, libraries, or packages you're unsure about, use the appropriate tool
- If information is beyond your training data or you need current/factual information, USE THE TOOLS
- Don't say you don't have information - try using search_wikipedia first!"""


# Define tools for Bikram.AI
@tool
def search_wikipedia(query: str) -> str:
    """Search Wikipedia for information about ANY topic including recent events, news, current affairs, technologies, concepts, or general knowledge. 
    Use this tool when:
    - Users ask about events from 2024-2025 or recent news
    - You need factual information beyond your training data
    - Users ask about specific incidents, explosions, accidents, or current events
    - You're unsure about any factual information
    
    Always try this tool before saying you don't have information!"""
    global _wikipedia
    if _wikipedia is None:
        _wikipedia = WikipediaAPIWrapper()
    try:
        result = _wikipedia.run(query)
        if "Page" in result and "does not exist" in result:
            # Try alternative search terms
            return f"No exact Wikipedia page found for '{query}'. The information might be under a different title or may not be available yet on Wikipedia."
        return result
    except Exception as e:
        return f"Error searching Wikipedia: {str(e)}"


@tool
def search_npm_package(package_name: str) -> str:
    """Get detailed information about an npm package including description, latest version, homepage, and repository. Use this when users ask about JavaScript/Node.js packages."""
    try:
        response = requests.get(f"https://registry.npmjs.org/{package_name}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            latest_version = data.get('dist-tags', {}).get('latest', 'N/A')
            description = data.get('description', 'No description available')
            homepage = data.get('homepage', 'N/A')
            repository = data.get('repository', {})
            repo_url = repository.get('url', 'N/A') if isinstance(repository, dict) else repository
            
            return f"""Package: {package_name}
Description: {description}
Latest Version: {latest_version}
Homepage: {homepage}
Repository: {repo_url}
NPM Link: https://www.npmjs.com/package/{package_name}"""
        else:
            return f"Package '{package_name}' not found on npm registry."
    except Exception as e:
        return f"Error fetching npm package info: {str(e)}"


@tool
def search_pypi_package(package_name: str) -> str:
    """Get information about a Python package from PyPI including description, latest version, and project URLs. Use this when users ask about Python packages."""
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            info = data.get('info', {})
            name = info.get('name', package_name)
            version = info.get('version', 'N/A')
            summary = info.get('summary', 'No summary available')
            home_page = info.get('home_page', 'N/A')
            project_url = info.get('project_url', f"https://pypi.org/project/{package_name}")
            
            return f"""Package: {name}
Summary: {summary}
Latest Version: {version}
Homepage: {home_page}
PyPI Link: {project_url}"""
        else:
            return f"Package '{package_name}' not found on PyPI."
    except Exception as e:
        return f"Error fetching PyPI package info: {str(e)}"


@tool
def get_mdn_docs(search_query: str) -> str:
    """Search MDN Web Docs for JavaScript, HTML, CSS, and web API documentation. Use this when users ask about web development concepts, APIs, or syntax."""
    try:
        # Use MDN's search API
        search_url = f"https://developer.mozilla.org/api/v1/search?q={search_query}"
        response = requests.get(search_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            documents = data.get('documents', [])
            
            if documents:
                # Get the top 3 most relevant results
                results = []
                for doc in documents[:3]:
                    title = doc.get('title', 'N/A')
                    summary = doc.get('summary', 'No summary available')
                    url = f"https://developer.mozilla.org{doc.get('mdn_url', '')}"
                    results.append(f"**{title}**\n{summary}\nURL: {url}")
                
                return "\n\n".join(results)
            else:
                return f"No MDN documentation found for '{search_query}'."
        else:
            return f"Could not search MDN docs at this time."
    except Exception as e:
        return f"Error searching MDN docs: {str(e)}"


def _get_agent():
    """Lazy initialization of the Bikram.AI agent."""
    global _agent
    
    if _agent is None:
        # Create model with Bikram's personality settings
        model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash", 
            temperature=0.8,  # Slightly more creative and personable
        )

        # Create tools list with developer-focused utilities
        tools = [
            search_wikipedia,
            search_npm_package,
            search_pypi_package,
            get_mdn_docs
        ]
        
        # Create agent with Bikram's personality and tools
        _agent = create_agent(
            model, 
            tools,
            system_prompt=BIKRAM_SYSTEM_PROMPT
        )
    
    return _agent


def get_bikram_ai_response(user_message: str) -> str:
    """
    Get response from Bikram.AI - A personalized AI assistant reflecting Bikram Mondal's personality.
    
    Args:
        user_message (str): The user's input message
        
    Returns:
        str: The AI's response in Bikram's friendly and helpful style, with markdown converted to HTML
    """
    try:
        agent = _get_agent()
        response = agent.invoke({
            "messages": [{"role": "user", "content": user_message}]
        })
        
        # Extract the final AI message
        markdown_output = None
        if response and "messages" in response and len(response["messages"]) > 0:
            # Find the last AI message with content
            for message in reversed(response["messages"]):
                if hasattr(message, 'content') and message.content and message.__class__.__name__ == 'AIMessage':
                    markdown_output = message.content
                    break
            
            if not markdown_output:
                markdown_output = "I couldn't process that request properly. Please try rephrasing your question!"
        else:
            markdown_output = "No response content found. Please try again."
        
        # Convert markdown to HTML with code syntax highlighting (same as Codestral 2501)
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
        return f"Error: {str(e)}"


# For testing in terminal (when run directly)
if __name__ == "__main__":
    print("Running Bikram.AI agent with tools...")
    
    # Test 1: General coding question
    print("\n" + "="*80)
    print("TEST 1: General Coding Question")
    print("="*80)
    test_message_1 = "Hey! Can you help me understand how to build a React app with Three.js?"
    print(f"\nUser: {test_message_1}")
    response_1 = get_bikram_ai_response(test_message_1)
    print(f"\nBikram.AI: {response_1[:500]}...")  # Print first 500 chars
    
    # Test 2: Package information (should use npm tool)
    print("\n" + "="*80)
    print("TEST 2: Package Information (Testing npm tool)")
    print("="*80)
    test_message_2 = "What is the latest version of react package and what does it do?"
    print(f"\nUser: {test_message_2}")
    response_2 = get_bikram_ai_response(test_message_2)
    print(f"\nBikram.AI: {response_2[:500]}...")  # Print first 500 chars
    
    print("\n" + "="*80)
    print("Testing complete!")
    print("="*80)
