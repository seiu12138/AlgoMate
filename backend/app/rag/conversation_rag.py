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
    
    def __init__(self, vector_store, llm, distance_threshold: float = 0.5, min_confidence: float = 0.3, enable_vector_storage: bool = False):
        """
        初始化 ConversationRAG

        Args:
            vector_store: 向量数据库实例
            llm: 大语言模型实例
            distance_threshold: 距离阈值（L2距离），默认 0.5，越小表示越相似
            min_confidence: 最小置信度，默认 0.3
        """
        self.vector_store = vector_store
        self.llm = llm
        self.session_manager = get_session_manager()
        self.distance_threshold = distance_threshold  # L2 距离阈值
        self.min_confidence = min_confidence
        self.enable_vector_storage = enable_vector_storage  # 是否启用向量存储
        
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
                # Check distance scores (L2 distance: smaller = more similar)
                for doc, distance in similar_docs:
                    if distance < self.distance_threshold:
                        return {
                            "shouldStore": False,
                            "confidenceScore": 1.0 - distance,  # Convert to confidence
                            "reason": f"Duplicate found (L2 distance={distance:.2f})"
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
                
                print(f"[VectorDB] Relevance check: is_relevant={is_relevant}, confidence={confidence:.2f}, threshold={self.min_confidence}, will_store={should_store}")
                
                return {
                    "shouldStore": should_store,
                    "confidenceScore": confidence,
                    "reason": result.get("reason", "")
                }
            except json.JSONDecodeError:
                # Default to storing if parsing fails
                print(f"[VectorDB] Relevance check: JSON parsing failed, defaulting to store")
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
        
        # Truncate query to fit embedding model limit (2048 tokens)
        # Chinese characters may need 2-3 tokens each, so use conservative limit
        max_chars = 1500
        if len(query) > max_chars:
            print(f"[VectorDB] Truncating search query: {len(query)} -> {max_chars} chars")
            query = query[:max_chars]
        
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
        
        # 2. Store message in vector DB if enabled and not skipped
        if self.enable_vector_storage and not skip_vector_store:
            should_store = True
            confidence_score = 1.0
            
            # For assistant messages, check relevance
            if role == "assistant":
                relevance_check = await self.should_store_in_vector_db(message)
                should_store = relevance_check["shouldStore"]
                confidence_score = relevance_check["confidenceScore"]
                message_obj["metadata"] = {
                    "isRelevantToAlgorithm": should_store,
                    "confidenceScore": confidence_score,
                    "vectorStored": should_store
                }
            
            if should_store:
                try:
                    await self._add_to_vector_store(
                        text=message,
                        session_id=session_id,
                        confidence_score=confidence_score,
                        role=role
                    )
                    print(f"[VectorDB] Successfully stored {role} message ({len(message)} chars)")
                except Exception as e:
                    print(f"[VectorDB] Failed to store {role} message: {e}")
            else:
                print(f"[VectorDB] Skipped storing {role} message (did not pass relevance check)")
        
        # 3. Add to session storage
        self.session_manager.add_message(session_id, message_obj)
        
        return message_obj
    
    async def process_message_async(
        self, 
        session_id: str, 
        message: str, 
        role: str = "assistant"
    ) -> None:
        """
        异步处理消息并存储到向量数据库（后台任务，不阻塞主流程）
        
        特点：
        - 只存储助手回复，忽略用户消息
        - 存储前进行相似度检查（去重）
        - 允许数据丢失，异常被静默处理
        
        Args:
            session_id: 会话ID
            message: 消息内容（应为助手回复）
            role: 角色，必须为 "assistant"
        """
        # Only store assistant messages and only if vector storage is enabled
        if role != "assistant" or not self.enable_vector_storage:
            return
        
        try:
            # 1. Check for duplicates via similarity search
            similar_docs = await self._async_similarity_search(message, k=1)
            if similar_docs:
                # Extract distance from result tuple (doc, distance)
                # L2 distance: smaller = more similar
                distance = similar_docs[0][1] if isinstance(similar_docs[0], tuple) else float('inf')
                if distance < self.distance_threshold:
                    print(f"[VectorDB] Skip storing (duplicate found, L2 distance={distance:.2f})")
                    return
            
            # 2. Check relevance
            relevance_check = await self.should_store_in_vector_db(message)
            if not relevance_check["shouldStore"]:
                print(f"[VectorDB] Skip storing (not relevant, confidence={relevance_check['confidenceScore']:.2f})")
                return
            
            # 3. Store in vector DB
            await self._add_to_vector_store(
                text=message,
                session_id=session_id,
                confidence_score=relevance_check["confidenceScore"],
                role=role
            )
            print(f"[VectorDB] Stored assistant response ({len(message)} chars)")
            
        except Exception as e:
            # Silently fail - data loss is acceptable for background storage
            print(f"[VectorDB] Failed to store (ignored): {e}")
    
    async def _add_to_vector_store(self, text: str, session_id: str, confidence_score: float, role: str = "assistant"):
        """
        将文本添加到向量数据库（支持分块存储）

        Args:
            text: 文本内容
            session_id: 会话ID
            confidence_score: 置信度分数
            role: 角色（"user" 或 "assistant"）
        """
        import asyncio
        loop = asyncio.get_event_loop()
        
        # Split text into chunks if too long (max 1500 chars per chunk)
        max_chars = 1500
        chunks = []
        
        if len(text) <= max_chars:
            chunks = [text]
        else:
            # Split by paragraphs first, then by sentences if needed
            paragraphs = text.split('\n\n')
            current_chunk = ""
            
            for para in paragraphs:
                if len(current_chunk) + len(para) + 2 <= max_chars:
                    current_chunk += (para + '\n\n')
                else:
                    # Save current chunk if not empty
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    
                    # If paragraph itself is too long, split by sentences
                    if len(para) > max_chars:
                        sentences = para.replace('。', '。|').replace('. ', '.|').split('|')
                        current_chunk = ""
                        for sent in sentences:
                            if len(current_chunk) + len(sent) + 1 <= max_chars:
                                current_chunk += (sent + ' ')
                            else:
                                if current_chunk:
                                    chunks.append(current_chunk.strip())
                                current_chunk = sent + ' '
                    else:
                        current_chunk = para + '\n\n'
            
            # Don't forget the last chunk
            if current_chunk:
                chunks.append(current_chunk.strip())
        
        # Store each chunk with metadata
        texts = []
        metadatas = []
        base_metadata = {
            "sessionId": session_id,
            "type": "conversation",
            "source": f"rag_{role}",
            "role": role,
            "confidenceScore": confidence_score,
            "timestamp": datetime.now().isoformat(),
            "totalChunks": len(chunks)
        }
        
        for i, chunk in enumerate(chunks):
            texts.append(chunk)
            metadata = base_metadata.copy()
            metadata["chunkIndex"] = i + 1
            metadata["isPartial"] = len(chunks) > 1
            metadatas.append(metadata)
        
        await loop.run_in_executor(
            None,
            lambda: self.vector_store.add_texts(texts, metadatas)
        )
        
        if len(chunks) > 1:
            print(f"[VectorDB] Stored {len(chunks)} chunks (total {len(text)} chars)")
        else:
            print(f"[VectorDB] Stored 1 chunk ({len(text)} chars)")
    
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
