"""
Bikram.AI - A RAG-powered AI assistant based on Bikram Mondal's personality and resume.

This package provides a modular implementation of Bikram.AI that uses:
- RAG pipeline for retrieving information from Bikram's resume
- LangChain agents with custom tools
- Gemini 2.0 Flash for generation
"""

from .agent import get_bikram_ai_response

__all__ = ['get_bikram_ai_response']
