#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Web search retriever with source tracking.
"""
from typing import List, Optional
from datetime import datetime

from langchain_core.documents import Document

from ..tools.web_search import WebSearchTool, web_search
from .base import BaseRetriever, SourceMetadata, SourceTaggedDocument, RetrievalResult


class WebRetriever(BaseRetriever):
    """
    网页检索器 (带来源标记)
    
    功能：
    1. 执行网页搜索
    2. 抓取网页内容
    3. 自动标记来源为 "web_search"
    4. 保留URL、标题等元数据
    """
    
    def __init__(
        self,
        provider: str = "duckduckgo",
        api_key: Optional[str] = None,
        max_results: int = 5,
        fetch_content: bool = True,
        cache_ttl: int = 3600
    ):
        """
        初始化网页检索器
        
        Args:
            provider: 搜索提供商 (duckduckgo/bing)
            api_key: API密钥 (Bing必需)
            max_results: 最大结果数
            fetch_content: 是否抓取网页正文
            cache_ttl: 缓存时间(秒)
        """
        self.search_tool = WebSearchTool(
            provider=provider,
            api_key=api_key,
            max_results=max_results,
            cache_ttl=cache_ttl
        )
        self.max_results = max_results
        self.fetch_content = fetch_content
    
    async def retrieve(self, query: str, k: int = None) -> RetrievalResult:
        """
        从网页搜索检索
        
        Args:
            query: 查询文本
            k: 返回结果数量
            
        Returns:
            带来源标记的检索结果
        """
        k = k or self.max_results
        
        # 执行搜索并抓取内容
        search_results = await self.search_tool.search_and_fetch(
            query,
            fetch_content=self.fetch_content
        )
        
        # 限制结果数量
        search_results = search_results[:k]
        
        # 转换为SourceTaggedDocument
        documents = []
        for result in search_results:
            source_meta = SourceMetadata(
                source_type="web_search",
                source_url=result.url,
                source_title=result.title,
                doc_id=None,  # 网页结果无doc_id
                score=result.timestamp,  # 用时间戳暂代
                timestamp=datetime.now().isoformat()
            )
            
            # 使用抓取的内容或摘要
            content = result.content or result.snippet
            
            tagged_doc = SourceTaggedDocument(
                page_content=content,
                source_metadata=source_meta,
                metadata={
                    "url": result.url,
                    "title": result.title,
                    "snippet": result.snippet,
                    "source": result.source
                }
            )
            documents.append(tagged_doc)
        
        return RetrievalResult(
            documents=documents,
            sources=["web_search"],
            vector_results=[],
            web_results=documents,
            needs_web_search=True
        )
    
    async def retrieve_with_fallback(
        self,
        query: str,
        k: int = None,
        min_content_length: int = 100
    ) -> RetrievalResult:
        """
        带降级的网页检索
        
        如果内容抓取失败，使用摘要作为降级
        
        Args:
            query: 查询文本
            k: 返回结果数
            min_content_length: 最小内容长度
            
        Returns:
            检索结果
        """
        result = await self.retrieve(query, k)
        
        # 检查内容长度，不足的用摘要补充
        for doc in result.documents:
            if len(doc.page_content) < min_content_length:
                snippet = doc.metadata.get('snippet', '')
                if snippet and len(snippet) > len(doc.page_content):
                    doc.page_content = snippet
        
        return result


# 便捷函数
async def web_retrieve(
    query: str,
    provider: str = "duckduckgo",
    api_key: Optional[str] = None,
    max_results: int = 5,
    fetch_content: bool = True
) -> RetrievalResult:
    """
    便捷的网页检索函数
    
    Args:
        query: 查询文本
        provider: 搜索提供商
        api_key: API密钥
        max_results: 最大结果数
        fetch_content: 是否抓取内容
        
    Returns:
        检索结果
    """
    retriever = WebRetriever(
        provider=provider,
        api_key=api_key,
        max_results=max_results,
        fetch_content=fetch_content
    )
    return await retriever.retrieve(query)
