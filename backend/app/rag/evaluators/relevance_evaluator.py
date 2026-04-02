#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Retrieval quality evaluator for hybrid RAG.
Assesses whether local retrieval results are sufficient to answer the query.
"""
import json
from dataclasses import dataclass
from typing import List, Optional

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate


@dataclass
class RetrievalEvaluation:
    """检索质量评估结果"""
    coverage_score: float  # 覆盖率 (0-1)
    relevance_score: float  # 相关性 (0-1)
    overall_score: float  # 综合评分 (0-1)
    needs_web_search: bool  # 是否需要网页搜索
    reason: str  # 评估理由
    
    @property
    def is_sufficient(self) -> bool:
        """本地知识是否充足"""
        return self.overall_score >= 0.7


class RelevanceEvaluator:
    """
    检索质量评估器
    
    评估维度：
    1. 覆盖率：检索结果覆盖问题的程度
    2. 相关性：结果与问题的语义匹配度
    3. 置信度：综合评分
    
    决策阈值：
    - score >= 0.7: 本地知识充足
    - 0.4 <= score < 0.7: 需要网页搜索补充
    - score < 0.4: 严重依赖网页搜索
    """
    
    # 默认评估Prompt
    DEFAULT_PROMPT = """请评估以下检索结果是否足够回答用户的问题。

## 用户问题
{question}

## 检索结果
{retrieved_documents}

请从以下维度评估：
1. 覆盖率 (coverage_score): 检索结果是否覆盖了问题的主要知识点？
   - 1.0: 完全覆盖，包含所有必要信息
   - 0.5: 部分覆盖，缺少一些细节
   - 0.0: 几乎无关

2. 相关性 (relevance_score): 检索结果与问题的相关程度？
   - 1.0: 高度相关，直接回答问题
   - 0.5: 有一定关联，但需要推断
   - 0.0: 完全不相关

3. 是否需要网页搜索 (needs_web_search):
   - true: 本地知识不足，需要搜索补充
   - false: 本地知识足够

请以JSON格式输出：
{{
    "coverage_score": 0.0-1.0,
    "relevance_score": 0.0-1.0,
    "overall_score": 0.0-1.0,
    "needs_web_search": true/false,
    "reason": "评估理由，说明为什么需要或不需要网页搜索"
}}"""
    
    def __init__(
        self,
        llm,
        prompt: Optional[str] = None,
        local_only_threshold: float = 0.7,
        web_search_threshold: float = 0.4
    ):
        """
        初始化评估器
        
        Args:
            llm: 大语言模型实例
            prompt: 自定义评估Prompt (可选)
            local_only_threshold: 仅使用本地知识的阈值
            web_search_threshold: 触发网页搜索的阈值
        """
        self.llm = llm
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", prompt or self.DEFAULT_PROMPT),
            ("user", "{question}")
        ])
        self.local_only_threshold = local_only_threshold
        self.web_search_threshold = web_search_threshold
    
    async def evaluate(
        self,
        question: str,
        documents: List[Document]
    ) -> RetrievalEvaluation:
        """
        评估检索质量
        
        Args:
            question: 用户问题
            documents: 检索到的文档列表
            
        Returns:
            评估结果
        """
        # 格式化文档
        doc_text = self._format_documents(documents)
        
        # 构建评估Prompt
        chain = self.prompt_template | self.llm
        
        try:
            response = await chain.ainvoke({
                "question": question,
                "retrieved_documents": doc_text
            })
            
            # 解析JSON响应
            result = self._parse_response(response.content)
            
            # 计算是否需要网页搜索
            needs_web = self._determine_needs_web_search(result["overall_score"])
            
            return RetrievalEvaluation(
                coverage_score=result["coverage_score"],
                relevance_score=result["relevance_score"],
                overall_score=result["overall_score"],
                needs_web_search=needs_web,
                reason=result["reason"]
            )
            
        except Exception as e:
            # 评估失败时，保守策略：触发网页搜索
            return RetrievalEvaluation(
                coverage_score=0.0,
                relevance_score=0.0,
                overall_score=0.0,
                needs_web_search=True,
                reason=f"评估过程出错: {str(e)}，默认触发网页搜索"
            )
    
    def _format_documents(self, documents: List[Document]) -> str:
        """格式化文档列表为文本"""
        if not documents:
            return "无检索结果"
        
        formatted = []
        for i, doc in enumerate(documents, 1):
            content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
            # 截断过长内容
            if len(content) > 500:
                content = content[:500] + "..."
            
            source = "未知"
            if hasattr(doc, 'metadata') and doc.metadata:
                source = doc.metadata.get('source', '未知')
            
            formatted.append(f"[{i}] 来源: {source}\n内容: {content}")
        
        return "\n\n".join(formatted)
    
    def _parse_response(self, content: str) -> dict:
        """解析LLM响应"""
        try:
            # 尝试直接解析JSON
            return json.loads(content)
        except json.JSONDecodeError:
            # 尝试从文本中提取JSON
            import re
            
            # 查找JSON代码块
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except:
                    pass
            
            # 查找花括号包裹的内容
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except:
                    pass
            
            # 解析失败，返回默认值
            return {
                "coverage_score": 0.0,
                "relevance_score": 0.0,
                "overall_score": 0.0,
                "needs_web_search": True,
                "reason": "无法解析评估结果，默认触发网页搜索"
            }
    
    def _determine_needs_web_search(self, overall_score: float) -> bool:
        """
        根据综合评分判断是否需要网页搜索
        
        Args:
            overall_score: 综合评分 (0-1)
            
        Returns:
            是否需要网页搜索
        """
        return overall_score < self.local_only_threshold
    
    async def evaluate_batch(
        self,
        queries: List[str],
        documents_list: List[List[Document]]
    ) -> List[RetrievalEvaluation]:
        """
        批量评估多个查询
        
        Args:
            queries: 查询列表
            documents_list: 对应每个查询的文档列表
            
        Returns:
            评估结果列表
        """
        import asyncio
        
        tasks = [
            self.evaluate(q, docs)
            for q, docs in zip(queries, documents_list)
        ]
        
        return await asyncio.gather(*tasks)


class SimpleRelevanceEvaluator:
    """
    简单检索质量评估器 (基于启发式规则，无需LLM)
    
    适用于：
    - 快速评估场景
    - LLM调用受限场景
    - 作为LLM评估的预筛选
    """
    
    def __init__(
        self,
        local_only_threshold: float = 0.7,
        min_document_count: int = 2
    ):
        self.local_only_threshold = local_only_threshold
        self.min_document_count = min_document_count
    
    def evaluate(
        self,
        question: str,
        documents: List[Document],
        scores: Optional[List[float]] = None
    ) -> RetrievalEvaluation:
        """
        基于启发式规则评估
        
        规则：
        1. 文档数量 >= min_document_count
        2. 平均相似度分数 >= threshold
        """
        if not documents:
            return RetrievalEvaluation(
                coverage_score=0.0,
                relevance_score=0.0,
                overall_score=0.0,
                needs_web_search=True,
                reason="无检索结果"
            )
        
        # 基于分数计算
        if scores and len(scores) > 0:
            avg_score = sum(scores) / len(scores)
            # 转换相似度分数到0-1范围 (假设分数是L2距离)
            relevance = max(0, min(1, 1 - avg_score))
        else:
            # 无分数时基于文档数量估算
            relevance = min(1.0, len(documents) / self.min_document_count)
        
        # 覆盖率基于文档数量
        coverage = min(1.0, len(documents) / self.min_document_count)
        
        # 综合分数 (简单平均)
        overall = (relevance + coverage) / 2
        
        needs_web = overall < self.local_only_threshold
        
        reason = (
            f"检索到 {len(documents)} 个文档, "
            f"相关性: {relevance:.2f}, 覆盖率: {coverage:.2f}, "
            f"综合: {overall:.2f}"
        )
        
        return RetrievalEvaluation(
            coverage_score=coverage,
            relevance_score=relevance,
            overall_score=overall,
            needs_web_search=needs_web,
            reason=reason
        )


# 便捷函数
async def evaluate_retrieval_quality(
    question: str,
    documents: List[Document],
    llm,
    **kwargs
) -> RetrievalEvaluation:
    """
    便捷的检索质量评估函数
    
    Args:
        question: 用户问题
        documents: 检索文档
        llm: 大语言模型
        **kwargs: 其他参数
        
    Returns:
        评估结果
    """
    evaluator = RelevanceEvaluator(llm, **kwargs)
    return await evaluator.evaluate(question, documents)
