#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Knowledge persister for asynchronous storage of web content to vector DB.
"""
import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any
from uuid import uuid4

from langchain_core.documents import Document


@dataclass
class KnowledgeItem:
    """知识项"""
    content: str  # 正文内容
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据
    doc_id: Optional[str] = None  # 文档ID
    
    def __post_init__(self):
        if self.doc_id is None:
            self.doc_id = str(uuid4())


class KnowledgePersister:
    """
    知识异步持久化器
    
    职责：
    1. 批量异步写入向量库
    2. 元数据标注
    3. 失败重试
    4. 队列管理
    """
    
    def __init__(
        self,
        vector_store,
        batch_size: int = 5,
        flush_interval: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        初始化持久化器
        
        Args:
            vector_store: 向量数据库实例
            batch_size: 批量写入大小
            flush_interval: 自动刷新间隔(秒)
            max_retries: 最大重试次数
            retry_delay: 重试延迟(秒)
        """
        self.vector_store = vector_store
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # 待处理队列
        self._queue: List[KnowledgeItem] = []
        self._lock = asyncio.Lock()
        self._flush_task: Optional[asyncio.Task] = None
        self._running = False
    
    async def start(self):
        """启动后台刷新任务"""
        self._running = True
        if self._flush_task is None:
            self._flush_task = asyncio.create_task(self._background_flush())
    
    async def stop(self):
        """停止并刷新剩余数据"""
        self._running = False
        
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
        
        # 刷新剩余数据
        await self.flush()
    
    async def schedule_persist(self, item: KnowledgeItem):
        """
        安排持久化任务
        
        Args:
            item: 知识项
        """
        async with self._lock:
            self._queue.append(item)
            
            # 达到批量阈值立即刷新
            if len(self._queue) >= self.batch_size:
                await self._flush_unlocked()
    
    async def flush(self):
        """立即刷新队列"""
        async with self._lock:
            await self._flush_unlocked()
    
    async def _flush_unlocked(self):
        """内部刷新实现 (需持有锁)"""
        if not self._queue:
            return
        
        items = self._queue[:]
        self._queue = []
        
        try:
            await self._persist_batch(items)
        except Exception as e:
            print(f"[KnowledgePersister] Batch persist failed: {e}")
            # 失败时重新入队
            self._queue.extend(items)
    
    async def _background_flush(self):
        """后台定期刷新"""
        while self._running:
            try:
                await asyncio.sleep(self.flush_interval)
                await self.flush()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[KnowledgePersister] Background flush error: {e}")
    
    async def _persist_batch(self, items: List[KnowledgeItem]):
        """
        批量持久化
        
        Args:
            items: 知识项列表
        """
        if not items:
            return
        
        # 准备数据
        texts = []
        metadatas = []
        
        for item in items:
            # 添加标准元数据
            enriched_metadata = self._enrich_metadata(item)
            
            texts.append(item.content)
            metadatas.append(enriched_metadata)
        
        # 写入向量库 (带重试)
        for attempt in range(self.max_retries):
            try:
                await self._write_to_vector_db(texts, metadatas)
                print(f"[KnowledgePersister] Persisted {len(items)} items")
                break
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"[KnowledgePersister] Retry {attempt + 1}/{self.max_retries}: {e}")
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise
    
    def _enrich_metadata(self, item: KnowledgeItem) -> Dict[str, Any]:
        """
        丰富元数据
        
        添加标准字段：
        - 来源信息
        - 处理信息
        - 质量评分
        - 生命周期
        """
        metadata = item.metadata.copy()
        
        # 标准字段
        standard_fields = {
            # 来源信息
            "source": metadata.get("source", "web_search"),
            "source_url": metadata.get("source_url", ""),
            "source_title": metadata.get("source_title", ""),
            "search_query": metadata.get("search_query", ""),
            
            # 处理信息
            "doc_id": item.doc_id,
            "ingestion_time": datetime.now().isoformat(),
            "ingestion_version": "1.0",
            "auto_ingested": True,
            
            # 质量评分
            "density_score": metadata.get("density_score", 0.0),
            "quality_score": metadata.get("quality_score", 0.0),
            "overall_score": metadata.get("overall_score", 0.0),
            
            # 内容分类
            "content_type": metadata.get("content_type", "algorithm_solution"),
            "algorithm_name": metadata.get("algorithm_name", ""),
            "tags": metadata.get("tags", []),
            "language": metadata.get("language", ""),
            
            # 去重信息
            "content_hash": metadata.get("content_hash", ""),
            
            # 生命周期
            "access_count": 0,
            "last_accessed": None,
            "needs_review": metadata.get("overall_score", 0.0) < 0.6
        }
        
        # 合并用户元数据
        metadata.update(standard_fields)
        
        return metadata
    
    async def _write_to_vector_db(self, texts: List[str], metadatas: List[Dict]):
        """
        写入向量数据库
        
        Args:
            texts: 文本列表
            metadatas: 元数据列表
        """
        loop = asyncio.get_event_loop()
        
        await loop.run_in_executor(
            None,
            lambda: self.vector_store.add_texts(texts, metadatas)
        )
    
    async def persist_single(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        持久化单个知识项
        
        Args:
            content: 内容
            metadata: 元数据
            
        Returns:
            文档ID
        """
        item = KnowledgeItem(
            content=content,
            metadata=metadata or {}
        )
        
        await self.schedule_persist(item)
        await self.flush()  # 立即刷新
        
        return item.doc_id
    
    def get_queue_size(self) -> int:
        """获取队列大小"""
        return len(self._queue)
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "queue_size": len(self._queue),
            "batch_size": self.batch_size,
            "flush_interval": self.flush_interval,
            "running": self._running
        }


class ImmediatePersister:
    """
    立即持久化器 (同步写入，无队列)
    
    适用于：
    - 低延迟要求场景
    - 数据量小场景
    - 测试环境
    """
    
    def __init__(self, vector_store):
        self.vector_store = vector_store
    
    async def persist(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        立即持久化
        
        Args:
            content: 内容
            metadata: 元数据
            
        Returns:
            文档ID
        """
        doc_id = str(uuid4())
        
        # 准备元数据
        enriched_metadata = {
            "doc_id": doc_id,
            "ingestion_time": datetime.now().isoformat(),
            "auto_ingested": True,
            **(metadata or {})
        }
        
        # 写入
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.vector_store.add_texts([content], [enriched_metadata])
        )
        
        return doc_id


# 便捷函数
async def persist_knowledge(
    content: str,
    vector_store,
    metadata: Optional[Dict[str, Any]] = None,
    **kwargs
) -> str:
    """
    便捷的知识持久化函数
    
    Args:
        content: 内容
        vector_store: 向量数据库
        metadata: 元数据
        **kwargs: 其他参数
        
    Returns:
        文档ID
    """
    persister = ImmediatePersister(vector_store)
    return await persister.persist(content, metadata)
