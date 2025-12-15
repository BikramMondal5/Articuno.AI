"""
RAG integration for Bikram.AI to query Bikram's resume from the knowledge base.
"""

import os
import importlib.util
from pathlib import Path

# Calculate absolute path to RAG directory
RAG_DIR = Path(__file__).parent.parent.parent / "RAG"
RAG_DIR_ABS = RAG_DIR.resolve()

# Flag to track if RAG is available
RAG_AVAILABLE = False
embed_query = None
query_vectorstore = None
genai = None
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RAG_TOP_K = 5

# Try to import RAG dependencies using importlib
try:
    # Load embeddings module
    embeddings_path = RAG_DIR_ABS / "app" / "utils" / "embeddings.py"
    spec_embeddings = importlib.util.spec_from_file_location("rag_embeddings", embeddings_path)
    embeddings_module = importlib.util.module_from_spec(spec_embeddings)
    spec_embeddings.loader.exec_module(embeddings_module)
    embed_query = embeddings_module.embed_query
    
    # Load config module
    config_path = RAG_DIR_ABS / "app" / "config.py"
    spec_config = importlib.util.spec_from_file_location("rag_config", config_path)
    config_module = importlib.util.module_from_spec(spec_config)
    spec_config.loader.exec_module(config_module)
    
    # Load vectorstore module
    vectorstore_path = RAG_DIR_ABS / "app" / "utils" / "vectorstore.py"
    spec_vectorstore = importlib.util.spec_from_file_location("rag_vectorstore", vectorstore_path)
    vectorstore_module = importlib.util.module_from_spec(spec_vectorstore)
    
    # Create a mock app module with config that has the client
    import sys as _sys
    mock_app = type('module', (), {})()
    mock_app.config = config_module
    _sys.modules['app'] = mock_app
    _sys.modules['app.config'] = config_module
    
    try:
        spec_vectorstore.loader.exec_module(vectorstore_module)
        query_vectorstore = vectorstore_module.query_vectorstore
    finally:
        # Clean up mock modules
        if 'app' in _sys.modules:
            del _sys.modules['app']
        if 'app.config' in _sys.modules:
            del _sys.modules['app.config']
    
    # Import genai
    import google.generativeai as _genai
    genai = _genai
    
    RAG_AVAILABLE = True
    
except Exception as e:
    import traceback
    print(f"Warning: RAG dependencies not available: {e}")
    traceback.print_exc()
    RAG_AVAILABLE = False

# Try to import local config
try:
    from .config import RAG_TOP_K as _RAG_TOP_K, GEMINI_API_KEY as _GEMINI_API_KEY
    RAG_TOP_K = _RAG_TOP_K
    if _GEMINI_API_KEY:
        GEMINI_API_KEY = _GEMINI_API_KEY
except ImportError:
    pass


def query_bikram_resume(query: str) -> str:
    """
    Query Bikram's resume using the RAG pipeline.
    
    Args:
        query (str): The question or search query about Bikram
        
    Returns:
        str: Retrieved information from Bikram's resume
    """
    if not RAG_AVAILABLE:
        return "RAG system is not available. Please ensure RAG dependencies are installed."
    
    try:
        # 1. Embed the query
        query_embedding = embed_query(query)
        
        # 2. Retrieve relevant chunks from the resume
        results = query_vectorstore(query_embedding, n_results=RAG_TOP_K)
        
        # 3. Extract the retrieved text chunks
        retrieved_chunks = results.get('documents', [[]])[0] if results else []
        
        if not retrieved_chunks:
            return "I couldn't find relevant information in Bikram's resume for this query."
        
        # 4. Combine chunks into context
        context = "\n\n".join(retrieved_chunks)
        
        # 5. Use Gemini to synthesize the answer from the context
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            prompt = f"""Based on the following information from Bikram Mondal's resume, answer the question.
If the information is not in the resume, say so.

Resume Information:
{context}

Question: {query}

Answer (be concise and friendly):"""
            
            response = model.generate_content(prompt)
            return response.text
        else:
            # Fallback: return raw context if no API key
            return f"Here's what I found in Bikram's resume:\n\n{context}"
            
    except Exception as e:
        return f"Error querying resume: {str(e)}"


def is_rag_available() -> bool:
    """Check if RAG system is available."""
    return RAG_AVAILABLE
