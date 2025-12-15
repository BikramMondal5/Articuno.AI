from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import uvicorn

from app.ingest import ingest_pdf
from app.rag import rag_query

app = FastAPI(title="Gemini RAG System")

class IngestRequest(BaseModel):
    pdf_path: str

class QueryRequest(BaseModel):
    question: str

@app.post("/ingest")
async def ingest_endpoint(payload: IngestRequest):
    """
    Endpoint to ingest a PDF file.
    Payload example: { "pdf_path": "pdfs/sample.pdf" }
    """
    if not os.path.exists(payload.pdf_path):
        raise HTTPException(status_code=404, detail=f"File not found: {payload.pdf_path}")
    
    try:
        count = ingest_pdf(payload.pdf_path)
        return {"status": "indexed", "chunks": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_endpoint(payload: QueryRequest):
    """
    Endpoint to ask a question.
    Payload example: { "question": "What is the summary?" }
    """
    try:
        response = rag_query(payload.question)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
