# RAG System - Quick Reference

## 📁 Directory Structure

```
RAG/
├── pdfs/              # Place your PDF files here
│   └── resume.pdf     # Bikram's resume
├── db/                # ChromaDB vector store (auto-created)
├── app/               # RAG application code
│   ├── config.py      # Configuration
│   ├── ingest.py      # PDF ingestion logic
│   ├── rag.py         # RAG query logic
│   └── utils/         # Utility functions
├── ingest_all.py      # Batch ingestion script ⭐
└── clear_db.py        # Database clearing script
```

## 🚀 Quick Start

### 1. Ingest All PDFs

To ingest all PDF files from the `pdfs/` folder:

```bash
cd RAG
python ingest_all.py
```

This will:
- Find all `.pdf` files in the `pdfs/` folder
- Extract text from each PDF
- Chunk the text into manageable pieces
- Generate embeddings using Gemini
- Store in ChromaDB vector database

### 2. Ingest with Fresh Start

To clear the database and re-ingest everything:

```bash
cd RAG
python ingest_all.py --clear
```

⚠️ **Warning**: This will delete all existing documents!

### 3. Ingest Single PDF

To ingest a specific PDF file:

```python
from app.ingest import ingest_pdf

chunks = ingest_pdf("pdfs/your_document.pdf")
print(f"Ingested {chunks} chunks")
```

## 📝 Adding New Documents

### Step-by-Step:

1. **Add your PDF** to the `pdfs/` folder:
   ```bash
   # Copy your PDF
   cp /path/to/your/document.pdf RAG/pdfs/
   ```

2. **Run the ingestion script**:
   ```bash
   cd RAG
   python ingest_all.py
   ```

3. **Done!** Your document is now searchable via Bikram.AI

### Example:

```bash
# Tomorrow you add a new resume
cp ~/Downloads/bikram_resume_2025.pdf RAG/pdfs/

# Ingest all PDFs (including the new one)
cd RAG
python ingest_all.py
```

Output:
```
Found 2 PDF file(s) to ingest:
  - resume.pdf
  - bikram_resume_2025.pdf

============================================================
Starting ingestion for: RAG/pdfs/resume.pdf
Created 15 chunks.
Stored 15 chunks in ChromaDB.
✓ Successfully ingested resume.pdf: 15 chunks

============================================================
Starting ingestion for: RAG/pdfs/bikram_resume_2025.pdf
Created 18 chunks.
Stored 18 chunks in ChromaDB.
✓ Successfully ingested bikram_resume_2025.pdf: 18 chunks

============================================================
INGESTION COMPLETE
============================================================
Total PDFs processed: 2
  ✓ Successful: 2
  ✗ Failed: 0
Total chunks stored: 33
============================================================
```

## 🔍 Querying Documents

### Via Bikram.AI Agent:

```python
from agent.Bikram_AI import get_bikram_ai_response

# The agent will automatically use the RAG system
response = get_bikram_ai_response("What are Bikram's skills?")
print(response)
```

### Direct RAG Query:

```python
from app.rag import rag_query

result = rag_query("What programming languages does Bikram know?")
print(result['answer'])
```

## 🛠️ Maintenance

### Clear Database

To remove all documents and start fresh:

```bash
cd RAG
python clear_db.py
```

### Check Database Status

```python
from app.utils.vectorstore import get_collection

collection = get_collection()
docs = collection.get()
print(f"Total documents: {len(docs['ids'])}")
```

## 📊 How It Works

1. **PDF Extraction**: Uses PyPDF2 to extract text from PDFs
2. **Chunking**: Splits text into ~500 character chunks with overlap
3. **Embedding**: Uses Gemini's `text-embedding-004` model
4. **Storage**: Stores in ChromaDB with persistent storage
5. **Retrieval**: Semantic search finds top-K relevant chunks
6. **Generation**: Gemini synthesizes natural answers from chunks

## 🔐 Configuration

Edit `app/config.py` to change:
- Database directory
- Collection name
- API keys

## 💡 Tips

1. **Supported Formats**: Currently only PDF files
2. **File Size**: No strict limit, but very large PDFs may take time
3. **Re-ingestion**: Running `ingest_all.py` again will add duplicates unless you use `--clear`
4. **Best Practice**: Use `--clear` when updating existing documents

## 🐛 Troubleshooting

### "No text extracted"
- Check if PDF is text-based (not scanned images)
- Try opening the PDF to verify it has selectable text

### "ChromaDB not initialized"
- Make sure you're running from the RAG directory
- Check that `.env` file has `GEMINI_API_KEY`

### "API quota exceeded"
- Wait for quota reset (usually 60 seconds)
- Consider using batch processing for large documents

## 📚 Examples

### Example 1: Update Resume

```bash
# Replace old resume
rm RAG/pdfs/resume.pdf
cp ~/Downloads/new_resume.pdf RAG/pdfs/resume.pdf

# Re-ingest with fresh start
cd RAG
python ingest_all.py --clear
```

### Example 2: Add Multiple Documents

```bash
# Add multiple PDFs
cp ~/Documents/*.pdf RAG/pdfs/

# Ingest all
cd RAG
python ingest_all.py
```

### Example 3: Verify Ingestion

```python
from app.utils.vectorstore import get_collection

collection = get_collection()
result = collection.query(
    query_embeddings=[[0.1] * 768],  # dummy query
    n_results=1
)
print(f"Sample document: {result['documents'][0][0][:100]}...")
```

---

**Need help?** Check the main project README or open an issue.
