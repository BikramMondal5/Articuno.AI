# Gemini RAG System

A complete Retrieval-Augmented Generation (RAG) system using Gemini 1.5 Pro, ChromaDB, and FastAPI.

## Features
- **PDF Ingestion**: Parses, chunks, and embeds PDF documents.
- **RAG Pipeline**: Retrieves relevant context and generates accurate answers using Gemini 1.5 Pro.
- **Vector Search**: Uses ChromaDB for efficient semantic search.
- **FastAPI Backend**: Provides `ingest` and `ask` endpoints.

## Prerequisites
1. Python 3.9+
2. A Google Cloud API Key for Gemini (Gemini 1.5 Pro enabled).

## Setup
1. **Clone/Open the project**.
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment**:
   - Open `.env` file.
   - Add your API Key: `GEMINI_API_KEY=your_actual_key_here`

## Running the Server
Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```
The server will start at `http://127.0.0.1:8000`.

## Usage

### 1. Ingest a PDF
Place your PDF files in the `pdfs/` directory.

**Endpoint**: `POST /ingest`
**Body**:
```json
{
    "pdf_path": "pdfs/yourdocument.pdf"
}
```
**Response**:
```json
{
    "status": "indexed",
    "chunks": 42
}
```

### 2. Ask a Question
**Endpoint**: `POST /ask`
**Body**:
```json
{
    "question": "What is the main topic of chapter 2?"
}
```
**Response**:
```json
{
    "answer": "The main topic of chapter 2 is..."
}
```

## Project Structure
```
project/
│── app/
│   │── main.py            # API Entry point
│   │── rag.py             # RAG Logic (Retrieval + Generation)
│   │── ingest.py          # Ingestion Logic (PDF -> VectorDB)
│   │── config.py          # Configuration & Database setup
│   │── utils/
│       │── pdf_loader.py  # PDF text extraction
│       │── chunker.py     # Text chunking
│       │── embeddings.py  # Gemini embeddings wrapper
│       │── vectorstore.py # ChromaDB wrapper
│── db/                    # Persistent Vector Database
│── pdfs/                  # Storage for input PDFs
│── requirements.txt
│── .env
│── README.md
```
