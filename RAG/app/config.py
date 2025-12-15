import os
import chromadb
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY not found in .env file.")

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Initialize ChromaDB Client
# Using PersistentClient as it is the modern replacement for the deprecated Settings(chroma_db_impl=...)
# This ensures data is saved to ./db
DB_DIR = "./db"
os.makedirs(DB_DIR, exist_ok=True)

client = chromadb.PersistentClient(path=DB_DIR)

print(f"ChromaDB initialized at {DB_DIR}")
