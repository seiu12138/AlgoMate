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
    retrieval_stage: str = "none"          # 检索阶段: "vector_db", "web_search", "none"
    
    def get_vector_db_count(self) -> int:
        """获取知识库结果数量"""
        return len([d for d in self.documents if d.source_metadata.source_type == "vector_db"])
    
    def get_web_search_count(self) -> int:
        """获取网页搜索结果数量"""
        return len([d for d in self.documents if d.source_metadata.source_type == "web_search"])
    
    def to_context_string(self) -> str:
        """
        转换为编号引用格式的上下文字符串
        
        格式:
        ## 参考资料
        [1] 内容摘要... (来源: 知识库)
        [2] 内容摘要... (来源: 网页 URL)
        
        用于构建 LLM Prompt 的上下文部分
        """
        if not self.documents:
            return ""
        
        parts = []
        parts.append("## 参考资料")
        
        # 所有文档统一编号 [1], [2], [3]...
        for i, doc in enumerate(self.documents, 1):
            # 构建来源信息
            if doc.source_metadata.source_type == "vector_db":
                source_info = "来自本地知识库"
            else:
                url = doc.source_metadata.source_url or "未知来源"
                source_info = f"来自网页 ({url})"
            
            # 截取内容摘要（前300字符）
            content_preview = doc.page_content[:300].replace('\n', ' ').strip()
            if len(doc.page_content) > 300:
                content_preview += "..."
            
            # 添加标题（如果有）
            title = doc.source_metadata.source_title or f"资料 {i}"
            
            parts.append(f"[{i}] {title}: {content_preview} ({source_info})")
        
        return "\n\n".join(parts)
    
    def to_citation_sources(self) -> List[Dict[str, Any]]:
        """
        转换为前端展示用的编号引用来源列表
        
        Returns:
            带编号的来源信息列表，格式:
            [
                {index: 1, type: "vector_db", title: "...", url: "...", preview: "..."},
                {index: 2, type: "web_search", title: "...", url: "...", preview: "..."}
            ]
        """
        sources = []
        for i, doc in enumerate(self.documents, 1):
            sources.append({
                "index": i,
                "type": doc.source_metadata.source_type,
                "title": doc.source_metadata.source_title or f"资料 {i}",
                "url": doc.source_metadata.source_url,
                "preview": doc.page_content[:200].replace('\n', ' ').strip(),
                "doc_id": doc.source_metadata.doc_id
            })
        return sources
    
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
