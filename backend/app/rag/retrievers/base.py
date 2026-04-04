#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Base classes for retrievers with source tracking.
"""
from dataclasses import dataclass, field
from typing import Literal, Optional, List, Dict, Any
from langchain_core.documents import Document


@dataclass
class SourceMetadata:
    """文档来源元数据"""
    source_type: Literal["vector_db", "web_search"]  # 来源类型
    source_url: Optional[str] = None                  # 原始URL（网页搜索时）
    source_title: Optional[str] = None                # 来源标题
    doc_id: Optional[str] = None                      # 文档ID（知识库时）
    score: Optional[float] = None                     # 相似度分数
    timestamp: Optional[str] = None                   # 收录时间
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "source_type": self.source_type,
            "source_url": self.source_url,
            "source_title": self.source_title,
            "doc_id": self.doc_id,
            "score": self.score,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SourceMetadata":
        """从字典创建"""
        return cls(**data)


class SourceTaggedDocument(Document):
    """
    带来源标记的文档
    
    继承自LangChain的Document，添加来源追踪功能
    """
    
    def __init__(
        self,
        page_content: str,
        source_metadata: SourceMetadata,
        metadata: Optional[Dict[str, Any]] = None
    ):
        # 合并元数据 - 将source_metadata存储在metadata字典中
        merged_metadata = metadata or {}
        merged_metadata["source_metadata"] = source_metadata.to_dict()
        
        super().__init__(page_content=page_content, metadata=merged_metadata)
    
    @property
    def source_metadata(self) -> SourceMetadata:
        """获取来源元数据"""
        meta_dict = self.metadata.get("source_metadata", {})
        return SourceMetadata.from_dict(meta_dict)
    
    def get_source_tag(self) -> str:
        """获取来源标记文本"""
        if self.source_metadata.source_type == "vector_db":
            return "[知识库检索]"
        else:
            return "[网页检索]"
    
    def get_formatted_source(self) -> str:
        """获取格式化的来源引用"""
        if self.source_metadata.source_type == "vector_db":
            return "[知识库检索]"
        else:
            url = self.source_metadata.source_url or "未知来源"
            title = self.source_metadata.source_title or "相关网页"
            return f"[网页检索] {title} (来源: {url})"
    
    def to_context_string(self) -> str:
        """
        转换为上下文字符串（用于Prompt）
        
        格式:
        [知识库检索] 内容...
        或
        [网页检索] 内容... (来源: URL)
        """
        tag = self.get_source_tag()
        content = self.page_content.strip()
        
        if self.source_metadata.source_type == "vector_db":
            return f"{tag}\n{content}"
        else:
            url = self.source_metadata.source_url or ""
            return f"{tag}\n{content}\n(来源: {url})"
    
    def to_frontend_source(self) -> Dict[str, Any]:
        """
        转换为前端展示用的来源信息
        """
        return {
            "type": self.source_metadata.source_type,
            "url": self.source_metadata.source_url,
            "title": self.source_metadata.source_title,
            "score": self.source_metadata.score,
            "doc_id": self.source_metadata.doc_id
        }


@dataclass
class RetrievalResult:
    """检索结果"""
    documents: List[SourceTaggedDocument]  # 文档列表
    sources: List[str]                     # 使用的来源类型列表
    vector_results: List[SourceTaggedDocument] = field(default_factory=list)  # 向量结果
    web_results: List[SourceTaggedDocument] = field(default_factory=list)     # 网页结果
    evaluation_score: Optional[float] = None  # 评估分数
    needs_web_search: bool = False         # 是否触发了网页搜索
    
    def get_vector_db_count(self) -> int:
        """获取知识库结果数量"""
        return len([d for d in self.documents if d.source_metadata.source_type == "vector_db"])
    
    def get_web_search_count(self) -> int:
        """获取网页搜索结果数量"""
        return len([d for d in self.documents if d.source_metadata.source_type == "web_search"])
    
    def to_context_string(self) -> str:
        """
        转换为完整的上下文字符串
        
        用于构建LLM Prompt的上下文部分
        """
        parts = []
        
        # 按来源分组
        vector_docs = [d for d in self.documents if d.source_metadata.source_type == "vector_db"]
        web_docs = [d for d in self.documents if d.source_metadata.source_type == "web_search"]
        
        if vector_docs:
            parts.append("## [知识库检索] 相关资料")
            for i, doc in enumerate(vector_docs, 1):
                parts.append(f"\n### 资料 {i}")
                parts.append(doc.page_content)
                parts.append(f"<!-- SOURCE: {doc.get_source_tag()} -->")
        
        if web_docs:
            parts.append("\n## [网页检索] 相关资料")
            for i, doc in enumerate(web_docs, 1):
                parts.append(f"\n### 资料 {i}")
                if doc.source_metadata.source_title:
                    parts.append(f"来源标题: {doc.source_metadata.source_title}")
                if doc.source_metadata.source_url:
                    parts.append(f"来源链接: {doc.source_metadata.source_url}")
                parts.append(f"内容:\n{doc.page_content}")
                parts.append(f"<!-- SOURCE: {doc.get_source_tag()} | URL: {doc.source_metadata.source_url} -->")
        
        return "\n\n".join(parts)
    
    def to_frontend_sources(self) -> List[Dict[str, Any]]:
        """转换为前端来源列表"""
        return [doc.to_frontend_source() for doc in self.documents]


class BaseRetriever:
    """检索器基类"""
    
    async def retrieve(self, query: str, k: int = 5) -> RetrievalResult:
        """
        检索接口
        
        Args:
            query: 查询文本
            k: 返回结果数量
            
        Returns:
            检索结果
        """
        raise NotImplementedError
    
    async def aretrieve(self, query: str, k: int = 5) -> RetrievalResult:
        """异步检索别名"""
        return await self.retrieve(query, k)
