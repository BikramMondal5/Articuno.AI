import google.generativeai as genai
import time

def embed_text(text: str) -> list[float]:
    """
    Embeds text using Gemini 'models/text-embedding-004'.
    """
    # Simple retry logic or error handling could be added here
    try:
        # Task type 'retrieval_document' is good for storing in vector db
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        print(f"Error embedding text: {e}")
        # Return empty list or raise, decided to re-raise for visibility during ingest
        raise e

def embed_query(text: str) -> list[float]:
    """
    Embeds query using Gemini 'models/text-embedding-004'.
    Task type 'retrieval_query' is appropriate for search queries.
    """
    try:
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_query"
        )
        return result['embedding']
    except Exception as e:
        print(f"Error embedding query: {e}")
        raise e
