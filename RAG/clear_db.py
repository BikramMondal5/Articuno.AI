import sys
import os

# Add the current directory to sys.path to ensure we can import 'app'
sys.path.append(os.getcwd())

from app.config import client

COLLECTION_NAME = "pdf_docs"

def clear_db():
    """
    Deletes the 'pdf_docs' collection from ChromaDB.
    This effectively clears all ingested documents.
    """
    print(f"Attempting to clear collection: '{COLLECTION_NAME}'...")
    
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print("✅ Success: Collection deleted. The database is now empty.")
    except ValueError:
        print(f"⚠️  Collection '{COLLECTION_NAME}' does not exist (it might have already been deleted).")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Confirmation prompt
    confirm = input("Are you sure you want to clear the Vector Database? This cannot be undone. (y/n): ")
    if confirm.lower() == 'y':
        clear_db()
    else:
        print("Operation cancelled.")
