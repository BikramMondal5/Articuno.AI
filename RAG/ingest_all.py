"""
Batch PDF Ingestion Script

This script ingests all PDF files from the pdfs/ directory into the ChromaDB vector store.
Run this whenever you add new PDFs to the pdfs/ folder.

Usage:
    python ingest_all.py
    
Options:
    --clear    Clear the database before ingesting (fresh start)
"""

import os
import sys
from pathlib import Path
from app.ingest import ingest_pdf
from app.utils.vectorstore import get_collection

def clear_database():
    """Clear all documents from the vector store."""
    try:
        collection = get_collection()
        # Get all IDs
        all_docs = collection.get()
        if all_docs and all_docs['ids']:
            collection.delete(ids=all_docs['ids'])
            print(f"✓ Cleared {len(all_docs['ids'])} existing documents from database")
        else:
            print("✓ Database is already empty")
    except Exception as e:
        print(f"Error clearing database: {e}")

def ingest_all_pdfs(clear_first=False):
    """
    Ingest all PDF files from the pdfs/ directory.
    
    Args:
        clear_first (bool): If True, clear the database before ingesting
    """
    # Get the pdfs directory
    pdfs_dir = Path(__file__).parent / "pdfs"
    
    if not pdfs_dir.exists():
        print(f"Error: pdfs directory not found at {pdfs_dir}")
        return
    
    # Find all PDF files
    pdf_files = list(pdfs_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {pdfs_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s) to ingest:")
    for pdf in pdf_files:
        print(f"  - {pdf.name}")
    print()
    
    # Clear database if requested
    if clear_first:
        print("Clearing existing database...")
        clear_database()
        print()
    
    # Ingest each PDF
    total_chunks = 0
    successful = 0
    failed = 0
    
    for pdf_file in pdf_files:
        try:
            print(f"{'='*60}")
            chunks = ingest_pdf(str(pdf_file))
            if chunks > 0:
                total_chunks += chunks
                successful += 1
                print(f"✓ Successfully ingested {pdf_file.name}: {chunks} chunks")
            else:
                failed += 1
                print(f"✗ Failed to ingest {pdf_file.name}: No chunks created")
        except Exception as e:
            failed += 1
            print(f"✗ Error ingesting {pdf_file.name}: {e}")
        print()
    
    # Summary
    print(f"{'='*60}")
    print(f"INGESTION COMPLETE")
    print(f"{'='*60}")
    print(f"Total PDFs processed: {len(pdf_files)}")
    print(f"  ✓ Successful: {successful}")
    print(f"  ✗ Failed: {failed}")
    print(f"Total chunks stored: {total_chunks}")
    print(f"{'='*60}")

if __name__ == "__main__":
    # Check for --clear flag
    clear_first = "--clear" in sys.argv
    
    if clear_first:
        print("⚠️  WARNING: This will clear all existing documents from the database!")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            sys.exit(0)
        print()
    
    ingest_all_pdfs(clear_first=clear_first)
