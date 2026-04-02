#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RAG retrievers with source tracking support.
"""
from .base import (
    BaseRetriever,
    SourceMetadata,
    SourceTaggedDocument,
    RetrievalResult
)
from .vector_retriever import VectorRetriever
from .web_retriever import WebRetriever, web_retrieve
from .hybrid_retriever import HybridRetriever, SimpleHybridRetriever, hybrid_retrieve

__all__ = [
    # Base
    "BaseRetriever",
    "SourceMetadata",
    "SourceTaggedDocument",
    "RetrievalResult",
    
    # Retrievers
    "VectorRetriever",
    "WebRetriever",
    "HybridRetriever",
    "SimpleHybridRetriever",
    
    # Utilities
    "web_retrieve",
    "hybrid_retrieve"
]
