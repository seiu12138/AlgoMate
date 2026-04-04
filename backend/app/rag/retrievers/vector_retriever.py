#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Vector database retriever with source tracking.
"""
import asyncio
from typing import List, Optional
from datetime import datetime

from langchain_core.documents import Document

from .base import BaseRetriever, SourceMetadata, SourceTaggedDocument, RetrievalResult


class VectorRetriever(BaseRetriever):
    """
    向量数据库检索器 (带来源标记)
    
    功能：
    1. 从本地向量数据库检索
    2. 自动标记来源为 "vector_db"
    3. 保留元数据（doc_id, score, timestamp等）
    """
    
    def __init__(self, vector_store, default_k: int = 5):
        """
        初始化向量检索器
        
        Args:
            vector_store: 向量数据库实例
            default_k: 默认返回结果数
        """
        self.vector_store = vector_store
        self.default_k = default_k
    
    async def retrieve(self, query: str, k: int = None) -> RetrievalResult:
        """
        从向量数据库检索
        
        Args:
            query: 查询文本
            k: 返回结果数量
            
        Returns:
            带来源标记的检索结果
        """
        k = k or self.default_k
        
        # 执行相似度搜索
        search_results = await self._async_similarity_search(query, k=k)
        
        # 转换为SourceTaggedDocument
        documents = []
        for doc, score in search_results:
            source_meta = self._extract_source_metadata(doc, score)
            tagged_doc = SourceTaggedDocument(
                page_content=doc.page_content if hasattr(doc, 'page_content') else str(doc),
                source_metadata=source_meta,
                metadata=doc.metadata if hasattr(doc, 'metadata') else {}
            )
            documents.append(tagged_doc)
        
        return RetrievalResult(
            documents=documents,
            sources=["vector_db"],
            vector_results=documents,
            web_results=[],
            needs_web_search=False
        )
    
    async def _async_similarity_search(
        self,
        query: str,
        k: int = 5
    ) -> List[tuple]:
        """
        异步相似度搜索（排除对话记录）
        
        Args:
            query: 查询文本
            k: 返回结果数
            
        Returns:
            (文档, 分数) 列表
        """
        loop = asyncio.get_event_loop()
        
        # 截断查询以避免超过embedding限制
        max_chars = 1500
        if len(query) > max_chars:
            query = query[:max_chars]
        
        # 先检索更多结果（因为后续会过滤掉一部分）
        results = await loop.run_in_executor(
            None,
            lambda: self.vector_store.similarity_search_with_score(query, k=k*3)
        )
        
        # 过滤掉对话记录（ChromaDB 不支持 $ne 操作符，需要后过滤）
        filtered_results = []
        for doc, score in results:
            metadata = doc.metadata if hasattr(doc, 'metadata') else {}
            doc_type = metadata.get('type', '')
            source = metadata.get('source', '')
            
            # 跳过对话记录（由 ConversationRAG 存储的）
            if doc_type == 'conversation' or 'rag_' in str(source).lower():
                continue
            filtered_results.append((doc, score))
        
        # 限制返回数量
        return filtered_results[:k]
    
    def _extract_source_metadata(
        self,
        doc: Document,
        score: float
    ) -> SourceMetadata:
        """
        从文档提取来源元数据
        
        Args:
            doc: LangChain文档
            score: 相似度分数
            
        Returns:
            来源元数据
        """
        metadata = doc.metadata if hasattr(doc, 'metadata') else {}
        
        return SourceMetadata(
            source_type="vector_db",
            doc_id=metadata.get('doc_id') or metadata.get('id'),
            score=score,
            timestamp=metadata.get('timestamp') or metadata.get('ingestion_time'),
            source_url=None,  # 本地知识库无URL
            source_title=metadata.get('source') or metadata.get('title', '本地知识库')
        )
    
    async def retrieve_with_filter(
        self,
        query: str,
        filter_dict: Optional[dict] = None,
        k: int = None
    ) -> RetrievalResult:
        """
        带过滤条件的检索（自动排除对话记录）
        
        Args:
            query: 查询文本
            filter_dict: 额外的过滤条件（ChromaDB 只支持简单的等值过滤）
            k: 返回结果数
            
        Returns:
            检索结果
        """
        k = k or self.default_k
        
        loop = asyncio.get_event_loop()
        
        # ChromaDB 只支持简单的等值过滤，复杂的过滤需要后处理
        # 先检索更多结果，然后过滤
        search_results = await loop.run_in_executor(
            None,
            lambda: self.vector_store.similarity_search_with_score(query, k=k*3)
        )
        
        # 转换为SourceTaggedDocument并过滤
        documents = []
        for doc, score in search_results:
            metadata = doc.metadata if hasattr(doc, 'metadata') else {}
            
            # 排除对话记录
            doc_type = metadata.get('type', '')
            source = metadata.get('source', '')
            if doc_type == 'conversation' or 'rag_' in str(source).lower():
                continue
            
            # 应用用户提供的额外过滤条件
            if filter_dict:
                match = True
                for key, value in filter_dict.items():
                    if metadata.get(key) != value:
                        match = False
                        break
                if not match:
                    continue
            
            source_meta = self._extract_source_metadata(doc, score)
            tagged_doc = SourceTaggedDocument(
                page_content=doc.page_content if hasattr(doc, 'page_content') else str(doc),
                source_metadata=source_meta,
                metadata=metadata
            )
            documents.append(tagged_doc)
            
            # 限制返回数量
            if len(documents) >= k:
                break
        
        return RetrievalResult(
            documents=documents,
            sources=["vector_db"],
            vector_results=documents,
            web_results=[],
            needs_web_search=False
        )
