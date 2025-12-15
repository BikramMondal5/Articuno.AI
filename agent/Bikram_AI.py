"""
Bikram.AI - Entry Point

This module provides the main entry point for Bikram.AI, a RAG-powered AI assistant
that reflects Bikram Mondal's personality and uses his resume as a knowledge base.

The implementation has been refactored into a modular structure:
- bikram_ai/config.py: Configuration and system prompts
- bikram_ai/tools.py: Tool definitions including RAG-powered resume search
- bikram_ai/rag_integration.py: RAG integration for querying Bikram's resume
- bikram_ai/agent.py: Main agent logic

This allows for better code organization and maintainability.
"""

import sys
import os
from pathlib import Path

# Add agent directory to path so we can import bikram_ai package
agent_dir = Path(__file__).parent
if str(agent_dir) not in sys.path:
    sys.path.insert(0, str(agent_dir))

from bikram_ai import get_bikram_ai_response

# Re-export for backward compatibility
__all__ = ['get_bikram_ai_response']



# For testing in terminal (when run directly)
if __name__ == "__main__":
    print("Running Bikram.AI agent with RAG-powered resume search...")
    print("=" * 80)
    
    # Test 1: Ask about Bikram's skills (should use RAG)
    print("\n" + "=" * 80)
    print("TEST 1: Bikram's Skills (Testing RAG resume search)")
    print("=" * 80)
    test_message_1 = "What are Bikram's technical skills and expertise?"
    print(f"\nUser: {test_message_1}")
    response_1 = get_bikram_ai_response(test_message_1)
    print(f"\nBikram.AI: {response_1[:500]}...")  # Print first 500 chars
    
    # Test 2: Ask about Bikram's projects (should use RAG)
    print("\n" + "=" * 80)
    print("TEST 2: Bikram's Projects (Testing RAG resume search)")
    print("=" * 80)
    test_message_2 = "Tell me about Bikram's projects and work experience"
    print(f"\nUser: {test_message_2}")
    response_2 = get_bikram_ai_response(test_message_2)
    print(f"\nBikram.AI: {response_2[:500]}...")  # Print first 500 chars
    
    # Test 3: General coding question (should use general knowledge)
    print("\n" + "=" * 80)
    print("TEST 3: General Coding Question")
    print("=" * 80)
    test_message_3 = "How do I build a React app with Three.js?"
    print(f"\nUser: {test_message_3}")
    response_3 = get_bikram_ai_response(test_message_3)
    print(f"\nBikram.AI: {response_3[:500]}...")  # Print first 500 chars
    
    # Test 4: Package information (should use npm tool)
    print("\n" + "=" * 80)
    print("TEST 4: Package Information (Testing npm tool)")
    print("=" * 80)
    test_message_4 = "What is the latest version of react package?"
    print(f"\nUser: {test_message_4}")
    response_4 = get_bikram_ai_response(test_message_4)
    print(f"\nBikram.AI: {response_4[:500]}...")  # Print first 500 chars
    
    print("\n" + "=" * 80)
    print("Testing complete!")
    print("=" * 80)
