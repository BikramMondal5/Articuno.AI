"""
Tool definitions for Bikram.AI agent.
"""

from langchain.tools import tool
from langchain_community.utilities import WikipediaAPIWrapper
import requests
from .rag_integration import query_bikram_resume, is_rag_available

# Lazy initialization
_wikipedia = None


@tool
def search_bikram_resume(query: str) -> str:
    """Search Bikram Mondal's resume for information about his skills, projects, education, experience, and background.
    
    Use this tool when users ask about:
    - Bikram's technical skills and technologies he knows
    - His projects and work experience
    - Educational background
    - Contact information
    - Professional achievements
    - Any personal information about Bikram
    
    This tool uses a RAG (Retrieval-Augmented Generation) system to search through Bikram's actual resume PDF."""
    
    if not is_rag_available():
        return "Resume search is currently unavailable. The RAG system needs to be configured."
    
    return query_bikram_resume(query)


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
            return f"No exact Wikipedia page found for '{query}'. The information might be under a different title or may not be available yet on Wikipedia."
        return result
    except Exception as e:
        return f"Error searching Wikipedia: {str(e)}"


@tool
def search_npm_package(package_name: str) -> str:
    """Get detailed information about an npm package including description, latest version, homepage, and repository. 
    
    Use this when users ask about JavaScript/Node.js packages."""
    
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
    """Get information about a Python package from PyPI including description, latest version, and project URLs. 
    
    Use this when users ask about Python packages."""
    
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
    """Search MDN Web Docs for JavaScript, HTML, CSS, and web API documentation. 
    
    Use this when users ask about web development concepts, APIs, or syntax."""
    
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


def get_all_tools():
    """Get all available tools for the Bikram.AI agent."""
    return [
        search_bikram_resume,
        search_wikipedia,
        search_npm_package,
        search_pypi_package,
        get_mdn_docs
    ]
