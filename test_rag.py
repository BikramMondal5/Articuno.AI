import sys
sys.path.insert(0, 'agent')

from bikram_ai.rag_integration import is_rag_available, query_bikram_resume

print(f"RAG Available: {is_rag_available()}")

if is_rag_available():
    print("\n✓ Testing RAG query...")
    result = query_bikram_resume("What are Bikram's main skills?")
    print(f"Result: {result[:200]}...")
else:
    print("\n✗ RAG not available")
