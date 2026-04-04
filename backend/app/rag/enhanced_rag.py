#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Enhanced RAG Service with hybrid retrieval, source tracking, and knowledge ingestion.

Features:
- Intelligent retrieval routing (vector DB + web search)
- Source tagging in responses ([知识库检索] / [网页检索])
- Automatic knowledge ingestion from web search results
- Async processing for non-blocking operation
"""
import asyncio
import json
from typing import AsyncGenerator, Dict, Any, Optional, List
from datetime import datetime

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings

from app.core.session_manager import get_session_manager
from utils.config_handler import model_conf
from utils.prompts_loader import (
    load_citation_generation_prompt,
    load_direct_generation_prompt
)

from .conversation_rag import ConversationRAG
from .retrievers.sequential_retriever import SequentialRetriever
from .retrievers.base import SourceTaggedDocument, RetrievalResult
from .ingestion.content_cleaner import ContentCleaner
from .ingestion.deduplicator import Deduplicator
from .ingestion.density_checker import DensityChecker
from .ingestion.knowledge_persister import KnowledgePersister, KnowledgeItem


class EnhancedRAGService:
    """
    增强版RAG服务
    
    特性：
    1. 智能混合检索 (本地知识库 + 网页搜索)
    2. 来源追踪与标注 ([知识库检索] / [网页检索])
    3. 知识自动沉淀 (高质量网页内容入库)
    4. 异步非阻塞处理
    """
    
    def __init__(
        self,
        vector_store=None,
        llm=None,
        web_search_provider: str = "duckduckgo",
        web_search_api_key: Optional[str] = None,
        enable_knowledge_ingestion: bool = True,
        local_only_threshold: float = 0.7,
        min_density_score: float = 0.75,
        dedup_threshold: float = 0.85
    ):
        """
        初始化增强RAG服务
        
        Args:
            vector_store: 向量数据库实例
            llm: 大语言模型实例
            web_search_provider: 网页搜索提供商
            web_search_api_key: 网页搜索API密钥
            enable_knowledge_ingestion: 是否启用知识沉淀
            local_only_threshold: 仅使用本地知识的阈值
            min_density_score: 知识入库最小密度分
            dedup_threshold: 去重阈值
        """
        # Initialize vector store and LLM if not provided
        if vector_store is None:
            from .vector_stores import VectorStoreService
            vector_store = VectorStoreService(
                embedding=DashScopeEmbeddings(model=model_conf['embedding_model_name'])
            )
        
        if llm is None:
            llm = ChatTongyi(model=model_conf['chat_model_name'])
        
        self.vector_store = vector_store
        self.llm = llm
        self.session_manager = get_session_manager()
        
        # Initialize sequential retriever (strict priority: RAG → Web → Direct)
        self.sequential_retriever = SequentialRetriever(
            vector_store=vector_store,
            llm=llm,
            min_vector_results=2,  # RAG至少需要2条结果才视为充足
            max_vector_results=5,
            max_web_results=5,
            web_search_provider=web_search_provider,
            web_search_api_key=web_search_api_key
        )
        
        # Initialize conversation RAG for session persistence
        # 禁用向量存储，避免对话历史污染知识库
        self.conversation_rag = ConversationRAG(vector_store, llm, enable_vector_storage=False)
        
        # Knowledge ingestion components
        self.enable_knowledge_ingestion = enable_knowledge_ingestion
        if enable_knowledge_ingestion:
            self.content_cleaner = ContentCleaner()
            self.deduplicator = Deduplicator(vector_store, similarity_threshold=dedup_threshold)
            self.density_checker = DensityChecker(llm, min_density_score=min_density_score)
            self.knowledge_persister = KnowledgePersister(vector_store)
        
        # Citation format prompt for numbered references [1][2]
        self.citation_prompt = ChatPromptTemplate.from_messages([
            ("system", load_citation_generation_prompt()),
        ])
        self.direct_prompt = ChatPromptTemplate.from_messages([
            ("system", load_direct_generation_prompt()),
        ])
        
        # Track async tasks
        self._background_tasks: set = set()
    
    async def chat(
        self,
        message: str,
        session_id: str,
        enable_web_search: bool = True,
        enable_source_tagging: bool = True
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式对话 (带来源标注)
        
        Args:
            message: 用户消息
            session_id: 会话ID
            enable_web_search: 是否启用网页搜索
            enable_source_tagging: 是否启用来源标注
            
        Yields:
            {
                "type": "source_info" | "token" | "done",
                "content": str,  # for token
                "sources": List[Dict]  # for source_info
            }
        """
        try:
            # Step 1: Sequential retrieval (RAG → Web → None)
            if enable_web_search:
                retrieval_result = await self.sequential_retriever.retrieve(message)
            else:
                # RAG only mode
                from .retrievers.vector_retriever import VectorRetriever
                vector_retriever = VectorRetriever(self.vector_store)
                rag_result = await vector_retriever.retrieve(message)
                # Mark as RAG stage if has results, else none
                from dataclasses import replace
                retrieval_result = replace(
                    rag_result,
                    retrieval_stage="vector_db" if rag_result.documents else "none"
                )
            
            # Step 2: Send source information first (with citation numbers)
            citation_sources = retrieval_result.to_citation_sources()
            yield {
                "type": "source_info",
                "sources": citation_sources,
                "summary": {
                    "total_count": len(citation_sources),
                    "vector_db_count": retrieval_result.get_vector_db_count(),
                    "web_search_count": retrieval_result.get_web_search_count(),
                    "retrieval_stage": retrieval_result.retrieval_stage
                }
            }
            
            # Step 3: Build context with sources
            context_with_sources = retrieval_result.to_context_string()
            
            # Step 4: Generate response with citation format [1][2]
            if retrieval_result.documents and enable_source_tagging:
                # 使用编号引用格式 Prompt，让 LLM 生成 [1][2] 角标
                chain = self.citation_prompt | self.llm | StrOutputParser()
                full_response = ""
                
                async for chunk in chain.astream({
                    "context": context_with_sources,
                    "question": message
                }):
                    full_response += chunk
                    yield {
                        "type": "token",
                        "content": chunk
                    }
            else:
                # 无检索结果，直接询问 LLM
                chain = self.direct_prompt | self.llm | StrOutputParser()
                full_response = ""
                
                async for chunk in chain.astream({
                    "question": message
                }):
                    full_response += chunk
                    yield {
                        "type": "token",
                        "content": chunk
                    }
            
            # Step 5: Trigger async knowledge ingestion (if web search was used)
            if enable_web_search and retrieval_result.needs_web_search and self.enable_knowledge_ingestion:
                task = asyncio.create_task(
                    self._ingest_web_results(
                        search_results=retrieval_result.web_results,
                        query=message
                    ),
                    name=f"knowledge_ingestion_{session_id[:8]}"
                )
                self._background_tasks.add(task)
                task.add_done_callback(self._background_tasks.discard)
            
            # Store conversation
            await self._store_conversation(session_id, message, full_response)
            
            yield {"type": "done"}
            
        except Exception as e:
            yield {
                "type": "error",
                "error": str(e)
            }
    
    def _extract_sources_info(self, retrieval_result: RetrievalResult) -> List[Dict[str, Any]]:
        """提取来源信息供前端展示"""
        return retrieval_result.to_frontend_sources()
    
    async def _ingest_web_results(
        self,
        search_results: List[SourceTaggedDocument],
        query: str
    ):
        """
        知识沉淀流程 (后台异步执行)
        
        流程：
        1. 内容清洗
        2. 去重检测
        3. 密度评估
        4. 异步存储
        """
        if not self.enable_knowledge_ingestion:
            return
        
        for doc in search_results:
            try:
                # Skip if no content
                if not doc.page_content or len(doc.page_content) < 200:
                    continue
                
                # Step 1: Content cleaning (simplified for already-fetched content)
                cleaned_content = doc.page_content
                
                # Step 2: Deduplication check
                duplicate_check = await self.deduplicator.is_duplicate(cleaned_content)
                if duplicate_check.is_duplicate:
                    continue
                
                # Step 3: Density evaluation
                density = await self.density_checker.evaluate(cleaned_content)
                
                if not density.should_store:
                    continue
                
                # Step 4: Build knowledge item
                knowledge_item = KnowledgeItem(
                    content=cleaned_content,
                    metadata={
                        "source": "web_search",
                        "source_url": doc.source_metadata.source_url,
                        "source_title": doc.source_metadata.source_title,
                        "search_query": query,
                        "density_score": density.overall_score,
                        "quality_score": density.quality_score,
                        "algorithm_name": doc.metadata.get("algorithm_name", ""),
                        "tags": density.suggested_tags,
                        "content_hash": duplicate_check.content_hash,
                        "ingestion_timestamp": datetime.now().isoformat()
                    }
                )
                
                # Step 5: Schedule persistence
                await self.knowledge_persister.schedule_persist(knowledge_item)
                
            except Exception as e:
                # Log but don't fail
                print(f"[KnowledgeIngestion] Failed to ingest {doc.source_metadata.source_url}: {e}")
                continue
    
    async def _store_conversation(self, session_id: str, user_message: str, assistant_response: str):
        """存储对话到会话管理器"""
        try:
            # Store user message
            await self.conversation_rag.process_message(
                session_id=session_id,
                message=user_message,
                role="user",
                skip_vector_store=False
            )
            
            # Store assistant response (async, non-blocking)
            asyncio.create_task(
                self.conversation_rag.process_message_async(
                    session_id=session_id,
                    message=assistant_response,
                    role="assistant"
                )
            )
        except Exception as e:
            print(f"[EnhancedRAG] Failed to store conversation: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        stats = {
            "knowledge_ingestion_enabled": self.enable_knowledge_ingestion,
            "background_tasks": len(self._background_tasks)
        }
        
        if self.enable_knowledge_ingestion:
            stats["queue_size"] = self.knowledge_persister.get_queue_size()
        
        return stats


# Singleton instance
_enhanced_rag_service: Optional[EnhancedRAGService] = None


def get_enhanced_rag_service(
    vector_store=None,
    llm=None,
    **kwargs
) -> EnhancedRAGService:
    """
    获取增强RAG服务单例
    
    Args:
        vector_store: 向量数据库实例
        llm: 大语言模型实例
        **kwargs: 其他配置参数
        
    Returns:
        EnhancedRAGService单例
    """
    global _enhanced_rag_service
    if _enhanced_rag_service is None:
        _enhanced_rag_service = EnhancedRAGService(
            vector_store=vector_store,
            llm=llm,
            **kwargs
        )
    return _enhanced_rag_service
