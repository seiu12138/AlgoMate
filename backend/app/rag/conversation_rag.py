#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Conversation RAG with smart vector storage.
Integrates session persistence with vector DB for enhanced context retrieval.
"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import uuid4

from langchain_core.prompts import ChatPromptTemplate

from app.core.session_manager import get_session_manager


class ConversationRAG:
    """
    RAG service with conversation persistence and smart vector storage.
    
    Features:
    - Stores all messages in session storage
    - Intelligently decides whether to store messages in vector DB
    - Retrieves from both vector DB and session history
    """
    
    def __init__(self, vector_store, llm, similarity_threshold: float = 0.85, min_confidence: float = 0.6):
        """
        初始化 ConversationRAG

        Args:
            vector_store: 向量数据库实例
            llm: 大语言模型实例
            similarity_threshold: 相似度阈值，默认 0.85
            min_confidence: 最小置信度，默认 0.6
        """
        self.vector_store = vector_store
        self.llm = llm
        self.session_manager = get_session_manager()
        self.similarity_threshold = similarity_threshold
        self.min_confidence = min_confidence
        
        # Prompt for relevance checking
        self.relevance_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an AI assistant that analyzes conversation content.
Your task is to determine if the content is relevant to algorithm learning.

Rate the relevance on a scale of 0-1 where:
- 1.0: Directly related to algorithms, data structures, coding problems
- 0.5: Somewhat related to programming or computer science
- 0.0: Completely unrelated (casual chat, greetings, etc.)

Respond with ONLY a JSON object:
{{
    "isRelevant": true/false,
    "confidenceScore": 0.0-1.0,
    "reason": "brief explanation"
}}"""),
            ("user", "Content: {content}")
        ])
    
    async def should_store_in_vector_db(self, content: str) -> Dict[str, Any]:
        """
        判断内容是否应该存入向量数据库

        逻辑：
        1. 检查与现有文档的相似度
        2. 如果相似度超过阈值，不存储
        3. 否则使用 LLM 判断相关性

        Args:
            content: 待判断的内容

        Returns:
            包含 shouldStore、confidenceScore、reason 的字典
        """
        try:
            # Retrieve similar documents
            similar_docs = await self._async_similarity_search(content, k=3)
            
            if similar_docs:
                # Check similarity scores from metadata
                for doc in similar_docs:
                    score = doc.get('score', 0)
                    if score > self.similarity_threshold:
                        return {
                            "shouldStore": False,
                            "confidenceScore": score,
                            "reason": f"High similarity ({score:.2f}) with existing content"
                        }
            
            # Use LLM to judge relevance
            chain = self.relevance_prompt | self.llm
            response = await chain.ainvoke({"content": content[:1000]})  # Limit content length
            
            try:
                result = json.loads(response.content)
                confidence = result.get("confidenceScore", 0)
                is_relevant = result.get("isRelevant", False)
                
                # Only store if relevant and confidence > threshold
                should_store = is_relevant and confidence > self.min_confidence
                
                return {
                    "shouldStore": should_store,
                    "confidenceScore": confidence,
                    "reason": result.get("reason", "")
                }
            except json.JSONDecodeError:
                # Default to storing if parsing fails
                return {
                    "shouldStore": True,
                    "confidenceScore": 0.5,
                    "reason": "Parsing failed, defaulting to store"
                }
                
        except Exception as e:
            # On error, default to not storing to avoid cluttering vector DB
            return {
                "shouldStore": False,
                "confidenceScore": 0,
                "reason": f"Error during check: {str(e)}"
            }
    
    async def _async_similarity_search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        异步相似度搜索包装器

        Args:
            query: 查询文本
            k: 返回结果数量，默认 3

        Returns:
            相似文档列表
        """
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            lambda: self.vector_store.similarity_search_with_score(query, k=k)
        )
    
    async def process_message(
        self, 
        session_id: str, 
        message: str, 
        role: str = "user",
        skip_vector_store: bool = False
    ) -> Dict[str, Any]:
        """
        处理消息：存入会话，可选存入向量数据库

        Args:
            session_id: 会话ID
            message: 消息内容
            role: 角色（"user" 或 "assistant"）
            skip_vector_store: 是否跳过向量存储检查

        Returns:
            包含向量存储决策的消息元数据
        """
        # 1. Create message object
        message_obj = {
            "role": role,
            "content": message,
            "metadata": {}
        }
        
        # 2. For assistant messages, check if should store in vector DB
        if role == "assistant" and not skip_vector_store:
            relevance_check = await self.should_store_in_vector_db(message)
            
            if relevance_check["shouldStore"]:
                # Store in vector DB with metadata
                try:
                    await self._add_to_vector_store(
                        text=message,
                        session_id=session_id,
                        confidence_score=relevance_check["confidenceScore"]
                    )
                except Exception as e:
                    print(f"Warning: Failed to store in vector DB: {e}")
            
            # Update message metadata
            message_obj["metadata"] = {
                "isRelevantToAlgorithm": relevance_check["shouldStore"],
                "confidenceScore": relevance_check["confidenceScore"],
                "vectorStored": relevance_check["shouldStore"]
            }
        
        # 3. Add to session storage
        self.session_manager.add_message(session_id, message_obj)
        
        return message_obj
    
    async def _add_to_vector_store(self, text: str, session_id: str, confidence_score: float):
        """
        将文本添加到向量数据库

        Args:
            text: 文本内容
            session_id: 会话ID
            confidence_score: 置信度分数
        """
        import asyncio
        loop = asyncio.get_event_loop()
        
        metadata = {
            "sessionId": session_id,
            "type": "conversation",
            "confidenceScore": confidence_score,
            "timestamp": datetime.now().isoformat()
        }
        
        await loop.run_in_executor(
            None,
            lambda: self.vector_store.add_texts([text], [metadata])
        )
    
    async def get_enhanced_context(
        self, 
        query: str, 
        session_id: str, 
        k: int = 3,
        max_history: int = 5
    ) -> str:
        """
        获取增强上下文（向量数据库 + 会话历史）

        Args:
            query: 查询文本
            session_id: 当前会话ID
            k: 向量数据库返回结果数量，默认 3
            max_history: 会话历史消息数量，默认 5

        Returns:
            合并后的上下文字符串
        """
        # 1. Retrieve from vector DB
        vector_results = []
        try:
            vector_results = await self._async_similarity_search(query, k=k)
        except Exception as e:
            print(f"Warning: Vector search failed: {e}")
        
        # 2. Retrieve from current session history
        session_history = ""
        try:
            session_data = self.session_manager.get_session(session_id)
            if session_data and session_data.get("messages"):
                # Get last N messages for context
                recent_messages = session_data["messages"][-max_history:]
                history_lines = []
                for msg in recent_messages:
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")
                    history_lines.append(f"{role}: {content[:200]}{'...' if len(content) > 200 else ''}")
                session_history = "\n".join(history_lines)
        except Exception as e:
            print(f"Warning: Failed to load session history: {e}")
        
        # 3. Combine contexts
        context_parts = []
        
        if vector_results:
            context_parts.append("## Relevant knowledge from database:")
            for doc, score in vector_results:
                content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
                context_parts.append(f"- {content[:300]}{'...' if len(content) > 300 else ''}")
        
        if session_history:
            context_parts.append("\n## Current conversation context:")
            context_parts.append(session_history)
        
        return "\n".join(context_parts) if context_parts else "No additional context available."
    
    async def generate_summary(self, first_message: str) -> str:
        """
        生成会话摘要标题

        Args:
            first_message: 第一条用户消息

        Returns:
            生成的标题（前30字符）
        """
        if not first_message or len(first_message.strip()) < 2:
            return "New Conversation"
        
        # Simple truncation strategy - use first 30 chars of user message
        # This is more reliable than LLM generation
        message = first_message.strip()
        if len(message) <= 30:
            return message
        return message[:30] + "..."


# Global instance for dependency injection
_conversation_rag: Optional[ConversationRAG] = None


def get_conversation_rag(vector_store=None, llm=None) -> ConversationRAG:
    """
    获取全局 ConversationRAG 实例

    Args:
        vector_store: 向量数据库实例（首次初始化必需）
        llm: 大语言模型实例（首次初始化必需）

    Returns:
        ConversationRAG 单例实例

    Raises:
        ValueError: 首次初始化时缺少必需参数
    """
    global _conversation_rag
    if _conversation_rag is None:
        if vector_store is None or llm is None:
            raise ValueError("vector_store and llm are required for first initialization")
        _conversation_rag = ConversationRAG(vector_store, llm)
    return _conversation_rag
