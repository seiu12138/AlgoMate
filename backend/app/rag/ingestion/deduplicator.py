#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Deduplicator for knowledge ingestion.
Detects duplicate content based on semantic similarity.
"""
import hashlib
from dataclasses import dataclass
from typing import List, Optional, Tuple

from langchain_core.documents import Document


@dataclass
class DuplicateCheckResult:
    """去重检查结果"""
    is_duplicate: bool  # 是否为重复内容
    content_hash: str  # 内容指纹
    similarity: float  # 最高相似度
    matched_doc_id: Optional[str] = None  # 匹配的文档ID
    reason: str = ""  # 判定理由


class Deduplicator:
    """
    知识库去重检测器
    
    策略：
    1. 向量相似度检索 (语义去重)
    2. 内容指纹比对 (精确去重)
    3. 阈值分层判断
    
    阈值说明：
    - similarity > 0.95: 精确重复，直接丢弃
    - 0.85 < similarity <= 0.95: 疑似重复，LLM判断
    - similarity <= 0.85: 新内容
    """
    
    def __init__(
        self,
        vector_store,
        similarity_threshold: float = 0.85,
        exact_match_threshold: float = 0.95,
        use_llm_for_suspected: bool = True
    ):
        """
        初始化去重检测器
        
        Args:
            vector_store: 向量数据库实例
            similarity_threshold: 相似度阈值 (疑似重复)
            exact_match_threshold: 精确匹配阈值
            use_llm_for_suspected: 疑似重复时是否使用LLM判断
        """
        self.vector_store = vector_store
        self.similarity_threshold = similarity_threshold
        self.exact_match_threshold = exact_match_threshold
        self.use_llm_for_suspected = use_llm_for_suspected
    
    async def is_duplicate(self, content: str) -> DuplicateCheckResult:
        """
        检查内容是否为重复
        
        Args:
            content: 待检查内容
            
        Returns:
            去重检查结果
        """
        # 计算内容指纹
        content_hash = self._compute_content_hash(content)
        
        # Step 1: 向量相似度搜索
        similar_docs = await self._search_similar(content, k=3)
        
        if not similar_docs:
            return DuplicateCheckResult(
                is_duplicate=False,
                content_hash=content_hash,
                similarity=0.0,
                reason="未找到相似文档"
            )
        
        # Step 2: 分析相似度
        max_similarity, best_match = self._analyze_similarity(similar_docs)
        
        # Step 3: 阈值判断
        if max_similarity > self.exact_match_threshold:
            # 精确重复
            return DuplicateCheckResult(
                is_duplicate=True,
                content_hash=content_hash,
                similarity=max_similarity,
                matched_doc_id=best_match,
                reason=f"精确重复 (相似度: {max_similarity:.3f})"
            )
        
        elif max_similarity > self.similarity_threshold:
            # 疑似重复
            if self.use_llm_for_suspected:
                # 可以在这里添加LLM判断逻辑
                # 简化处理：视为重复
                return DuplicateCheckResult(
                    is_duplicate=True,
                    content_hash=content_hash,
                    similarity=max_similarity,
                    matched_doc_id=best_match,
                    reason=f"疑似重复 (相似度: {max_similarity:.3f})"
                )
            else:
                return DuplicateCheckResult(
                    is_duplicate=True,
                    content_hash=content_hash,
                    similarity=max_similarity,
                    matched_doc_id=best_match,
                    reason=f"疑似重复 (相似度: {max_similarity:.3f}, 使用启发式规则)"
                )
        
        else:
            # 新内容
            return DuplicateCheckResult(
                is_duplicate=False,
                content_hash=content_hash,
                similarity=max_similarity,
                reason=f"新内容 (最高相似度: {max_similarity:.3f})"
            )
    
    def _compute_content_hash(self, content: str) -> str:
        """
        计算内容指纹
        
        使用SimHash或MinHash进行近似去重
        简化实现：使用MD5的变体
        """
        # 预处理：去除空白，统一大小写
        normalized = ' '.join(content.lower().split())
        
        # 使用MD5
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:32]
    
    async def _search_similar(
        self,
        content: str,
        k: int = 3
    ) -> List[Tuple[Document, float]]:
        """
        搜索相似文档
        
        Args:
            content: 查询内容
            k: 返回结果数
            
        Returns:
            (文档, 分数)列表
        """
        try:
            import asyncio
            
            loop = asyncio.get_event_loop()
            
            # 使用向量存储的相似度搜索
            # 注意：假设vector_store有similarity_search_with_score方法
            results = await loop.run_in_executor(
                None,
                lambda: self.vector_store.similarity_search_with_score(content, k=k)
            )
            
            return results
            
        except Exception as e:
            print(f"[Deduplicator] Similarity search failed: {e}")
            return []
    
    def _analyze_similarity(
        self,
        similar_docs: List[Tuple[Document, float]]
    ) -> Tuple[float, Optional[str]]:
        """
        分析相似度结果
        
        Args:
            similar_docs: 相似文档列表
            
        Returns:
            (最高相似度, 最佳匹配文档ID)
        """
        if not similar_docs:
            return 0.0, None
        
        max_similarity = 0.0
        best_match = None
        
        for doc, score in similar_docs:
            # 转换分数（假设是L2距离，越小越相似）
            # 归一化到0-1范围
            similarity = max(0.0, 1.0 - score)
            
            if similarity > max_similarity:
                max_similarity = similarity
                # 获取文档ID
                if hasattr(doc, 'metadata') and doc.metadata:
                    best_match = doc.metadata.get('doc_id') or doc.metadata.get('id')
        
        return max_similarity, best_match
    
    def compute_jaccard_similarity(self, text1: str, text2: str) -> float:
        """
        计算Jaccard相似度 (词集合)
        
        用于：
        - 精确去重辅助
        - 短文本相似度
        """
        # 分词 (简单按字符和词)
        def get_shingles(text: str, k: int = 3):
            """生成k-gram"""
            text = text.lower()
            return set(text[i:i+k] for i in range(len(text) - k + 1))
        
        shingles1 = get_shingles(text1)
        shingles2 = get_shingles(text2)
        
        if not shingles1 or not shingles2:
            return 0.0
        
        intersection = len(shingles1 & shingles2)
        union = len(shingles1 | shingles2)
        
        return intersection / union if union > 0 else 0.0
    
    async def find_similar_content(
        self,
        content: str,
        threshold: float = 0.7,
        k: int = 5
    ) -> List[Tuple[Document, float]]:
        """
        查找相似内容 (用于推荐或合并)
        
        Args:
            content: 查询内容
            threshold: 相似度阈值
            k: 最大结果数
            
        Returns:
            相似文档及相似度列表
        """
        similar_docs = await self._search_similar(content, k=k)
        
        results = []
        for doc, score in similar_docs:
            similarity = max(0.0, 1.0 - score)
            if similarity >= threshold:
                results.append((doc, similarity))
        
        return sorted(results, key=lambda x: x[1], reverse=True)


class SimpleDeduplicator:
    """
    简单去重器 (基于哈希，无向量数据库依赖)
    
    适用于：
    - 快速去重
    - 内存中去重
    - 无向量存储场景
    """
    
    def __init__(self, similarity_threshold: float = 0.9):
        self.similarity_threshold = similarity_threshold
        self._hashes: set = set()
    
    def is_duplicate(self, content: str) -> DuplicateCheckResult:
        """检查是否重复"""
        content_hash = hashlib.md5(
            ' '.join(content.lower().split()).encode()
        ).hexdigest()
        
        if content_hash in self._hashes:
            return DuplicateCheckResult(
                is_duplicate=True,
                content_hash=content_hash,
                similarity=1.0,
                reason="精确哈希匹配"
            )
        
        # 检查近似匹配
        for existing_hash in self._hashes:
            # 简化：只比较前16位
            if content_hash[:16] == existing_hash[:16]:
                return DuplicateCheckResult(
                    is_duplicate=True,
                    content_hash=content_hash,
                    similarity=0.8,
                    reason="近似哈希匹配"
                )
        
        self._hashes.add(content_hash)
        return DuplicateCheckResult(
            is_duplicate=False,
            content_hash=content_hash,
            similarity=0.0,
            reason="新内容"
        )
    
    def clear(self):
        """清空缓存"""
        self._hashes.clear()


# 便捷函数
async def check_duplicate(
    content: str,
    vector_store,
    **kwargs
) -> DuplicateCheckResult:
    """
    便捷的去重检查函数
    
    Args:
        content: 待检查内容
        vector_store: 向量数据库
        **kwargs: 其他参数
        
    Returns:
        去重结果
    """
    deduplicator = Deduplicator(vector_store, **kwargs)
    return await deduplicator.is_duplicate(content)
