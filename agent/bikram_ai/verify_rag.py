"""
Verification script for Bikram.AI RAG integration.

This script verifies that:
1. The RAG system is properly configured
2. Bikram's resume is ingested into the vector store
3. The resume search tool works correctly
4. The full agent can query the resume
"""

import sys
from pathlib import Path

# Add RAG directory to path
RAG_DIR = Path(__file__).parent.parent / "RAG"
sys.path.insert(0, str(RAG_DIR))

print("=" * 80)
print("Bikram.AI RAG Integration Verification")
print("=" * 80)

# Step 1: Check RAG dependencies
print("\n[1/5] Checking RAG dependencies...")
try:
    from app.utils.embeddings import embed_query
    from app.utils.vectorstore import query_vectorstore
    import google.generativeai as genai
    print("✓ All RAG dependencies are available")
except ImportError as e:
    print(f"✗ Missing RAG dependency: {e}")
    sys.exit(1)

# Step 2: Check if resume is ingested
print("\n[2/5] Checking if resume is ingested in vector store...")
try:
    test_query = "Bikram skills"
    test_embedding = embed_query(test_query)
    results = query_vectorstore(test_embedding, n_results=1)
    
    if results and results.get('documents') and len(results['documents'][0]) > 0:
        print("✓ Resume data found in vector store")
        print(f"  Sample chunk: {results['documents'][0][0][:100]}...")
    else:
        print("✗ No resume data found in vector store")
        print("  Please run the ingestion script first:")
        print("  cd RAG && python -m app.main")
        sys.exit(1)
except Exception as e:
    print(f"✗ Error querying vector store: {e}")
    sys.exit(1)

# Step 3: Test RAG integration module
print("\n[3/5] Testing RAG integration module...")
try:
    from bikram_ai.rag_integration import query_bikram_resume, is_rag_available
    
    if not is_rag_available():
        print("✗ RAG integration reports as unavailable")
        sys.exit(1)
    
    print("✓ RAG integration module loaded successfully")
    
    # Test a query
    test_result = query_bikram_resume("What are Bikram's main technical skills?")
    print(f"  Sample response: {test_result[:150]}...")
    
except Exception as e:
    print(f"✗ Error testing RAG integration: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Test the resume search tool
print("\n[4/5] Testing resume search tool...")
try:
    from bikram_ai.tools import search_bikram_resume
    
    # Invoke the tool
    tool_result = search_bikram_resume.invoke({"query": "What programming languages does Bikram know?"})
    print("✓ Resume search tool works correctly")
    print(f"  Tool response: {tool_result[:150]}...")
    
except Exception as e:
    print(f"✗ Error testing resume search tool: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 5: Test the full agent
print("\n[5/5] Testing full Bikram.AI agent...")
try:
    from bikram_ai import get_bikram_ai_response
    
    # Test with a question about Bikram
    response = get_bikram_ai_response("What are Bikram's top 3 technical skills?")
    
    if response and len(response) > 0:
        print("✓ Full agent works correctly")
        print(f"  Agent response preview: {response[:200]}...")
    else:
        print("✗ Agent returned empty response")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ Error testing full agent: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# All tests passed
print("\n" + "=" * 80)
print("✓ ALL VERIFICATION CHECKS PASSED!")
print("=" * 80)
print("\nBikram.AI is ready to use with RAG-powered resume search.")
print("\nYou can now:")
print("1. Run the agent: python agent/Bikram_AI.py")
print("2. Use it in your app: from agent.Bikram_AI import get_bikram_ai_response")
print("3. Ask questions about Bikram's skills, projects, and experience")
print("=" * 80)
