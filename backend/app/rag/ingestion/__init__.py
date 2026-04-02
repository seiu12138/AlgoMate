#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Knowledge ingestion pipeline for automatic knowledge base expansion.
"""
from .content_cleaner import ContentCleaner, CleanedContent, clean_web_content
from .deduplicator import Deduplicator, SimpleDeduplicator, DuplicateCheckResult, check_duplicate
from .density_checker import DensityChecker, DensityScore, evaluate_content_density
from .knowledge_persister import KnowledgePersister, ImmediatePersister, KnowledgeItem, persist_knowledge

__all__ = [
    # Content Cleaner
    "ContentCleaner",
    "CleanedContent",
    "clean_web_content",
    
    # Deduplicator
    "Deduplicator",
    "SimpleDeduplicator",
    "DuplicateCheckResult",
    "check_duplicate",
    
    # Density Checker
    "DensityChecker",
    "DensityScore",
    "evaluate_content_density",
    
    # Knowledge Persister
    "KnowledgePersister",
    "ImmediatePersister",
    "KnowledgeItem",
    "persist_knowledge"
]
