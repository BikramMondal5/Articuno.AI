import google.generativeai as genai
from app.utils.embeddings import embed_query
from app.utils.vectorstore import query_vectorstore

# Initialize specific model for generation
# We put this here to avoid circular imports or re-init issues, 
# though it could live in config if we wanted a global model object.
model = genai.GenerativeModel('gemini-2.5-flash')

def rag_query(query: str):
    """
    Performs RAG:
    1. Embed query
    2. Retrieve context
    3. Generate answer
    """
    
    # 1. Embed Query
    query_emb = embed_query(query)
    
    # 2. Retrieve top 5 chunks
    results = query_vectorstore(query_emb, n_results=5)
    
    # Flatten results (results['documents'] is List[List[str]])
    retrieved_chunks = results['documents'][0] if (results and results['documents']) else []
    
    if not retrieved_chunks:
        return {"answer": "I couldn't find any relevant information in the documents."}
        
    context_str = "\n\n".join(retrieved_chunks)
    
    # 3. Construct Prompt
    prompt = f"""
    Use ONLY the context below to answer the question.

    Context:
    {context_str}

    Query:
    {query}

    Answer:
    """
    
    # 4. Call Gemini
    try:
        response = model.generate_content(prompt)
        answer_text = response.text
        return {"answer": answer_text}
    except Exception as e:
        print(f"Error generating answer: {e}")
        return {"error": str(e)}
