#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Hybrid retriever with intelligent routing and source tracking.
Combines vector DB and web search with RRF fusion.
"""
from typing import List, Optional, Dict, Any
from collections import defaultdict

from ..evaluators.relevance_evaluator import RelevanceEvaluator, SimpleRelevanceEvaluator
from ..tools.web_search import WebSearchTool
from .base import BaseRetriever, SourceMetadata, SourceTaggedDocument, RetrievalResult
from .vector_retriever import VectorRetriever
from .web_retriever import WebRetriever


class HybridRetriever(BaseRetriever):
    """
    智能混合检索器 - 带来源追踪
    
    核心功能：
    1. 并行执行向量检索 + 异步准备网页搜索
    2. 使用LLM评估向量检索质量
    3. 根据评估结果决定是否触发网页搜索
    4. RRF (Reciprocal Rank Fusion) 融合多源结果
    5. 所有结果标记来源信息
    
    决策逻辑：
    - overall_score >= 0.7: 仅使用本地知识
    - 0.4 <= score < 0.7: 本地+网页搜索补充
    - score < 0.4: 主要依赖网页搜索
    """
    
    def __init__(
        self,
        vector_store,
        llm,
        web_search_provider: str = "duckduckgo",
        web_search_api_key: Optional[str] = None,
        local_only_threshold: float = 0.7,
        web_search_threshold: float = 0.4,
        max_vector_results: int = 5,
        max_web_results: int = 5,
        rrf_k: int = 60,
        use_llm_evaluation: bool = True
    ):
        """
        初始化混合检索器
        
        Args:
            vector_store: 向量数据库实例
            llm: 大语言模型实例
            web_search_provider: 网页搜索提供商
            web_search_api_key: 网页搜索API密钥
            local_only_threshold: 仅使用本地知识的阈值
            web_search_threshold: 触发网页搜索的阈值
            max_vector_results: 向量检索最大结果数
            max_web_results: 网页搜索最大结果数
            rrf_k: RRF算法参数
            use_llm_evaluation: 是否使用LLM评估
        """
        self.vector_retriever = VectorRetriever(vector_store, default_k=max_vector_results)
        self.web_retriever = WebRetriever(
            provider=web_search_provider,
            api_key=web_search_api_key,
            max_results=max_web_results
        )
        
        # 评估器
        if use_llm_evaluation and llm:
            self.evaluator = RelevanceEvaluator(
                llm,
                local_only_threshold=local_only_threshold,
                web_search_threshold=web_search_threshold
            )
        else:
            self.evaluator = SimpleRelevanceEvaluator(
                local_only_threshold=local_only_threshold
            )
        
        self.local_only_threshold = local_only_threshold
        self.web_search_threshold = web_search_threshold
        self.max_vector_results = max_vector_results
        self.max_web_results = max_web_results
        self.rrf_k = rrf_k
        self.use_llm_evaluation = use_llm_evaluation
    
    async def retrieve(self, query: str, k: int = 5) -> RetrievalResult:
        """
        智能混合检索
        
        Args:
            query: 查询文本
            k: 返回结果数量
            
        Returns:
            带来源标记的检索结果
        """
        # Step 1: 本地向量检索 (必做)
        vector_result = await self.vector_retriever.retrieve(query, k=self.max_vector_results)
        vector_docs = vector_result.documents
        
        # Step 2: 评估本地检索质量
        evaluation = await self.evaluator.evaluate(query, vector_docs)
        
        # Step 3: 根据评估结果决定策略
        if evaluation.overall_score >= self.local_only_threshold:
            # 本地知识充足
            return RetrievalResult(
                documents=vector_docs,
                sources=["vector_db"],
                vector_results=vector_docs,
                web_results=[],
                evaluation_score=evaluation.overall_score,
                needs_web_search=False
            )
        
        # Step 4: 本地知识不足，执行网页搜索
        web_result = await self.web_retriever.retrieve(query, k=self.max_web_results)
        web_docs = web_result.documents
        
        # Step 5: 融合结果
        if evaluation.overall_score >= self.web_search_threshold:
            # 本地知识尚可，融合两种来源
            fused_docs = self._rrf_fuse(vector_docs, web_docs, k=k)
            sources = ["vector_db", "web_search"]
        else:
            # 本地知识严重不足，主要依赖网页搜索
            # 但仍保留少量本地结果
            fused_docs = self._rrf_fuse(vector_docs, web_docs, k=k, web_weight=1.5)
            sources = ["web_search", "vector_db"]
        
        return RetrievalResult(
            documents=fused_docs,
            sources=sources,
            vector_results=vector_docs,
            web_results=web_docs,
            evaluation_score=evaluation.overall_score,
            needs_web_search=True
        )
    
    def _rrf_fuse(
        self,
        vector_docs: List[SourceTaggedDocument],
        web_docs: List[SourceTaggedDocument],
        k: int = 5,
        web_weight: float = 1.0
    ) -> List[SourceTaggedDocument]:
        """
        RRF (Reciprocal Rank Fusion) 融合算法
        
        公式: score = Σ(1 / (k + rank)) * weight
        
        Args:
            vector_docs: 向量检索结果
            web_docs: 网页搜索结果
            k: RRF参数，默认60
            web_weight: 网页结果权重
            
        Returns:
            融合排序后的文档列表
        """
        scores = defaultdict(float)
        doc_map = {}
        
        # 处理向量结果 (权重1.0)
        for rank, doc in enumerate(vector_docs):
            doc_id = doc.source_metadata.doc_id or f"vector_{rank}"
            scores[doc_id] += 1.0 / (self.rrf_k + rank + 1)
            doc_map[doc_id] = doc
        
        # 处理网页结果 (可调整权重)
        for rank, doc in enumerate(web_docs):
            doc_id = doc.source_metadata.source_url or f"web_{rank}"
            scores[doc_id] += (1.0 * web_weight) / (self.rrf_k + rank + 1)
            doc_map[doc_id] = doc
        
        # 按分数排序
        sorted_docs = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # 返回前k个
        return [doc_map[doc_id] for doc_id, _ in sorted_docs[:k]]
    
    def format_context_with_sources(
        self,
        retrieval_result: RetrievalResult
    ) -> str:
        """
        格式化带来源标记的上下文
        
        Args:
            retrieval_result: 检索结果
            
        Returns:
            格式化的上下文字符串
        """
        return retrieval_result.to_context_string()
    
    def get_source_summary(self, retrieval_result: RetrievalResult) -> Dict[str, Any]:
        """
        获取来源摘要信息
        
        Args:
            retrieval_result: 检索结果
            
        Returns:
            来源统计信息
        """
        return {
            "sources_used": retrieval_result.sources,
            "vector_db_count": retrieval_result.get_vector_db_count(),
            "web_search_count": retrieval_result.get_web_search_count(),
            "evaluation_score": retrieval_result.evaluation_score,
            "needs_web_search": retrieval_result.needs_web_search
        }


class SimpleHybridRetriever(BaseRetriever):
    """
    简单混合检索器 (无LLM评估，基于规则)
    
    适用于：
    - 快速原型
    - LLM调用受限场景
    - 成本控制
    """
    
    def __init__(
        self,
        vector_store,
        web_search_provider: str = "duckduckgo",
        web_search_api_key: Optional[str] = None,
        min_vector_results: int = 3,
        max_web_results: int = 3
    ):
        self.vector_retriever = VectorRetriever(vector_store)
        self.web_retriever = WebRetriever(
            provider=web_search_provider,
            api_key=web_search_api_key,
            max_results=max_web_results
        )
        self.min_vector_results = min_vector_results
        self.max_web_results = max_web_results
    
    async def retrieve(self, query: str, k: int = 5) -> RetrievalResult:
        """
        简单混合检索
        
        策略：
        - 始终执行向量检索
        - 如果向量结果 < min_vector_results，补充网页搜索
        """
        # 向量检索
        vector_result = await self.vector_retriever.retrieve(query, k=k)
        vector_docs = vector_result.documents
        
        # 检查是否需要网页搜索
        if len(vector_docs) >= self.min_vector_results:
            return RetrievalResult(
                documents=vector_docs,
                sources=["vector_db"],
                vector_results=vector_docs,
                web_results=[],
                needs_web_search=False
            )
        
        # 补充网页搜索
        web_result = await self.web_retriever.retrieve(query, k=self.max_web_results)
        web_docs = web_result.documents
        
        # 合并结果 (向量优先)
        combined = vector_docs + web_docs
        
        return RetrievalResult(
            documents=combined[:k],
            sources=["vector_db", "web_search"],
            vector_results=vector_docs,
            web_results=web_docs,
            needs_web_search=True
        )


# 便捷函数
async def hybrid_retrieve(
    query: str,
    vector_store,
    llm,
    **kwargs
) -> RetrievalResult:
    """
    便捷的混合检索函数
    
    Args:
        query: 查询文本
        vector_store: 向量数据库
        llm: 大语言模型
        **kwargs: 其他参数
        
    Returns:
        检索结果
    """
    retriever = HybridRetriever(vector_store, llm, **kwargs)
    return await retriever.retrieve(query)
