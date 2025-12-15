from app.config import client

COLLECTION_NAME = "pdf_docs"

def get_collection():
    """
    Get or create the ChromaDB collection.
    """
    return client.get_or_create_collection(name=COLLECTION_NAME)

def add_to_vectorstore(documents: list[str], embeddings: list[list[float]], ids: list[str]):
    """
    Add documents and their embeddings to the collection.
    """
    collection = get_collection()
    collection.add(
        documents=documents,
        embeddings=embeddings,
        ids=ids
    )

def query_vectorstore(query_embedding: list[float], n_results: int = 5):
    """
    Query the collection for top matching documents.
    """
    collection = get_collection()
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
