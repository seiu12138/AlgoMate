#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sequential retriever with strict priority order.

执行顺序:
1. 向量数据库检索 (RAG)
2. 如果 RAG 结果不足 → 网页搜索
3. 如果都无结果 → 返回空（直接询问 LLM）

特点:
- 严格控制流程，不会混合多个来源
- 根据实际使用的检索阶段标记来源
- 避免网页检索内容覆盖模型输出
"""
from typing import List, Optional

from .base import BaseRetriever, RetrievalResult
from .vector_retriever import VectorRetriever
from .web_retriever import WebRetriever


class SequentialRetriever(BaseRetriever):
    """
    顺序检索器 - 严格按优先级执行检索
    
    优先级:
    1. 本地知识库 (vector_db)
    2. 网页搜索 (web_search)
    3. 直接询问 LLM (none)
    
    配置参数:
    - min_vector_results: 触发网页搜索的最小 RAG 结果数
    - max_vector_results: RAG 最大结果数
    - max_web_results: 网页搜索最大结果数
    """
    
    def __init__(
        self,
        vector_store,
        llm=None,
        min_vector_results: int = 2,
        max_vector_results: int = 5,
        max_web_results: int = 5,
        web_search_provider: str = "duckduckgo",
        web_search_api_key: Optional[str] = None
    ):
        """
        初始化顺序检索器
        
        Args:
            vector_store: 向量数据库实例
            llm: 大语言模型实例（未使用，保留接口一致性）
            min_vector_results: 触发网页搜索的最小 RAG 结果数，默认 2
            max_vector_results: RAG 最大结果数，默认 5
            max_web_results: 网页搜索最大结果数，默认 5
            web_search_provider: 网页搜索提供商，默认 "duckduckgo"
            web_search_api_key: 网页搜索 API 密钥
        """
        self.vector_retriever = VectorRetriever(
            vector_store, 
            default_k=max_vector_results
        )
        self.web_retriever = WebRetriever(
            provider=web_search_provider,
            api_key=web_search_api_key,
            max_results=max_web_results
        )
        self.min_vector_results = min_vector_results
        self.max_vector_results = max_vector_results
        self.max_web_results = max_web_results
    
    async def retrieve(self, query: str, k: int = 5) -> RetrievalResult:
        """
        顺序检索
        
        执行流程:
        1. 先执行 RAG 检索
        2. 如果 RAG 结果数 >= min_vector_results，直接返回 RAG 结果
        3. 否则执行网页搜索
        4. 如果网页搜索有结果，返回网页结果
        5. 否则返回空结果
        
        Args:
            query: 查询文本
            k: 返回结果数量（实际返回数量可能少于 k）
            
        Returns:
            RetrievalResult，包含 retrieval_stage 标记当前检索阶段
        """
        # Step 1: RAG 检索
        vector_result = await self.vector_retriever.retrieve(query, k=self.max_vector_results)
        vector_docs = vector_result.documents
        
        # 检查 RAG 结果是否足够
        if len(vector_docs) >= self.min_vector_results:
            # RAG 结果充足，直接返回，不触发网页搜索
            return RetrievalResult(
                documents=vector_docs,
                sources=["vector_db"],
                vector_results=vector_docs,
                web_results=[],
                evaluation_score=1.0,  # RAG 结果充足，给满分
                needs_web_search=False,
                retrieval_stage="vector_db"
            )
        
        # Step 2: RAG 不足，执行网页搜索
        web_result = await self.web_retriever.retrieve(query, k=self.max_web_results)
        web_docs = web_result.documents
        
        if web_docs:
            # 网页搜索有结果，返回网页结果
            return RetrievalResult(
                documents=web_docs,
                sources=["web_search"],
                vector_results=[],  # 清空 RAG 结果，避免混合
                web_results=web_docs,
                evaluation_score=0.5,  # 网页搜索结果
                needs_web_search=True,
                retrieval_stage="web_search"
            )
        
        # Step 3: 都无结果
        return RetrievalResult(
            documents=[],
            sources=[],
            vector_results=[],
            web_results=[],
            evaluation_score=0.0,
            needs_web_search=False,
            retrieval_stage="none"
        )


class SimpleSequentialRetriever(BaseRetriever):
    """
    简单顺序检索器（基于规则的轻量版本）
    
    适用于:
    - 无需 LLM 评估的场景
    - 快速响应
    - 成本控制
    """
    
    def __init__(
        self,
        vector_store,
        min_vector_results: int = 1,
        max_vector_results: int = 3,
        max_web_results: int = 3,
        web_search_provider: str = "duckduckgo"
    ):
        self.vector_retriever = VectorRetriever(vector_store, default_k=max_vector_results)
        self.web_retriever = WebRetriever(
            provider=web_search_provider,
            max_results=max_web_results
        )
        self.min_vector_results = min_vector_results
        self.max_web_results = max_web_results
    
    async def retrieve(self, query: str, k: int = 5) -> RetrievalResult:
        """顺序检索（简化版）"""
        # Step 1: RAG
        vector_result = await self.vector_retriever.retrieve(query, k=k)
        
        if len(vector_result.documents) >= self.min_vector_results:
            return RetrievalResult(
                documents=vector_result.documents,
                sources=["vector_db"],
                vector_results=vector_result.documents,
                web_results=[],
                needs_web_search=False,
                retrieval_stage="vector_db"
            )
        
        # Step 2: Web search
        web_result = await self.web_retriever.retrieve(query, k=self.max_web_results)
        
        if web_result.documents:
            return RetrievalResult(
                documents=web_result.documents,
                sources=["web_search"],
                vector_results=[],
                web_results=web_result.documents,
                needs_web_search=True,
                retrieval_stage="web_search"
            )
        
        # Step 3: None
        return RetrievalResult(
            documents=[],
            sources=[],
            vector_results=[],
            web_results=[],
            needs_web_search=False,
            retrieval_stage="none"
        )
