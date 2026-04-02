#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Knowledge density evaluator for content quality assessment.
Determines if web content is worth storing in the knowledge base.
"""
import json
import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from langchain_core.prompts import ChatPromptTemplate

from utils.prompts_loader import load_density_eval_prompt


@dataclass
class DensityScore:
    """知识密度评分"""
    density_score: float  # 信息密度 (0-1)
    structure_score: float  # 结构完整度 (0-1)
    scarcity_score: float  # 知识稀缺性 (0-1)
    quality_score: float  # 质量置信度 (0-1)
    overall_score: float  # 综合评分 (0-1)
    should_store: bool  # 是否推荐存储
    reason: str  # 评估理由
    suggested_tags: List[str] = field(default_factory=list)  # 建议标签


class DensityChecker:
    """
    知识密度评估器
    
    评估维度：
    1. 信息密度：单位字符的有效信息量
    2. 结构完整度：是否有清晰的逻辑结构
    3. 知识稀缺性：是否包含独特见解
    4. 质量置信度：内容专业度和准确性
    
    决策阈值：
    - overall_score >= 0.75: 高密度，推荐存储
    - 0.5 <= overall_score < 0.75: 中密度，可选存储
    - overall_score < 0.5: 低密度，丢弃
    """
    
    def __init__(
        self,
        llm=None,
        prompt: Optional[str] = None,
        min_density_score: float = 0.75,
        min_quality_score: float = 0.60
    ):
        """
        初始化密度评估器
        
        Args:
            llm: 大语言模型实例 (可选，用于LLM评估)
            prompt: 自定义评估Prompt
            min_density_score: 最小密度阈值
            min_quality_score: 最小质量阈值
        """
        self.llm = llm
        self.min_density_score = min_density_score
        self.min_quality_score = min_quality_score
        
        if llm:
            # 从文件加载prompt，如失败则使用空字符串作为fallback
            try:
                default_prompt = load_density_eval_prompt()
            except Exception:
                default_prompt = ""
            
            self.prompt_template = ChatPromptTemplate.from_messages([
                ("system", prompt or default_prompt),
                ("user", "{content}")
            ])
        else:
            self.prompt_template = None
    
    async def evaluate(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DensityScore:
        """
        评估内容密度
        
        Args:
            content: 待评估内容
            metadata: 元数据信息 (可选)
            
        Returns:
            密度评分
        """
        # 如果提供了LLM，使用LLM评估
        if self.llm and self.prompt_template:
            return await self._llm_evaluate(content)
        else:
            # 使用启发式评估
            return self._heuristic_evaluate(content, metadata)
    
    async def _llm_evaluate(self, content: str) -> DensityScore:
        """使用LLM评估"""
        try:
            chain = self.prompt_template | self.llm
            
            # 截断过长内容
            truncated = content[:3000] if len(content) > 3000 else content
            
            response = await chain.ainvoke({"content": truncated})
            result = self._parse_response(response.content)
            
            return DensityScore(
                density_score=result["density_score"],
                structure_score=result["structure_score"],
                scarcity_score=result["scarcity_score"],
                quality_score=result["quality_score"],
                overall_score=result["overall_score"],
                should_store=result["should_store"],
                reason=result["reason"],
                suggested_tags=result.get("suggested_tags", [])
            )
            
        except Exception as e:
            # LLM评估失败，降级到启发式
            return self._heuristic_evaluate(content)
    
    def _heuristic_evaluate(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DensityScore:
        """
        启发式评估 (无需LLM)
        
        评分规则：
        - 代码块数量
        - 复杂度提及
        - 算法名称识别
        - 内容长度和结构
        """
        scores = {
            "density": 0.0,
            "structure": 0.0,
            "scarcity": 0.0,
            "quality": 0.0
        }
        
        # 1. 信息密度评分
        # 代码块
        code_blocks = re.findall(r'```[\s\S]*?```', content)
        if code_blocks:
            scores["density"] += min(0.4, len(code_blocks) * 0.15)
        
        # 复杂度分析
        if re.search(r'时间复杂度|空间复杂度|O\([\w\s\+\*]+\)', content, re.IGNORECASE):
            scores["density"] += 0.3
        
        # 算法名称
        algo_patterns = [
            r'(?:动态规划|贪心|回溯|分治|二分|递归|迭代|DFS|BFS|并查集|线段树|树状数组)',
            r'(?:Dynamic Programming|Greedy|Backtrack|Divide and Conquer|Binary Search)'
        ]
        for pattern in algo_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                scores["density"] += 0.15
                break
        
        scores["density"] = min(1.0, scores["density"])
        
        # 2. 结构完整度
        # 步骤说明
        steps = re.findall(r'(?:^|\n)(?:\d+[.．、]|步骤|Step)\s*\d*', content, re.MULTILINE)
        if steps:
            scores["structure"] += min(0.4, len(steps) * 0.1)
        
        # 段落结构
        paragraphs = [p for p in content.split('\n\n') if len(p.strip()) > 20]
        if len(paragraphs) >= 3:
            scores["structure"] += 0.3
        
        # 标题层级
        if re.search(r'^#{1,3}\s+', content, re.MULTILINE):
            scores["structure"] += 0.3
        
        scores["structure"] = min(1.0, scores["structure"])
        
        # 3. 知识稀缺性
        # 优化技巧
        if re.search(r'优化|Optimization|技巧|Trick|进阶|Advanced', content, re.IGNORECASE):
            scores["scarcity"] += 0.4
        
        # 复杂度对比
        if re.search(r'对比|比较|vs|versus|difference', content, re.IGNORECASE):
            scores["scarcity"] += 0.3
        
        # 示例丰富度
        examples = len(re.findall(r'例如|示例|Example|例如', content))
        scores["scarcity"] += min(0.3, examples * 0.1)
        
        scores["scarcity"] = min(1.0, scores["scarcity"])
        
        # 4. 质量置信度
        # 内容长度
        content_len = len(content)
        if content_len >= 1000:
            scores["quality"] += 0.3
        elif content_len >= 500:
            scores["quality"] += 0.2
        
        # 来源可靠性
        if metadata:
            source = metadata.get('source', '')
            if source in ['github', 'leetcode', 'wikipedia']:
                scores["quality"] += 0.3
            elif source in ['cnblogs', 'csdn', 'juejin']:
                scores["quality"] += 0.2
        
        # 公式或数学表达
        if re.search(r'[\$\[\(]?[OΩΘ][\(\)\w\s\+\-\*/\^]+[\$\]\)]?', content):
            scores["quality"] += 0.2
        
        # 代码注释
        commented_code = re.findall(r'# .+|// .+|/\* .*?\*/', content)
        if len(commented_code) >= 3:
            scores["quality"] += 0.2
        
        scores["quality"] = min(1.0, scores["quality"])
        
        # 计算综合分数
        overall = (
            scores["density"] * 0.35 +
            scores["structure"] * 0.25 +
            scores["scarcity"] * 0.20 +
            scores["quality"] * 0.20
        )
        
        # 决策
        should_store = (
            overall >= self.min_density_score and
            scores["quality"] >= self.min_quality_score
        )
        
        # 生成理由
        reason_parts = [
            f"信息密度: {scores['density']:.2f}",
            f"结构完整: {scores['structure']:.2f}",
            f"知识稀缺: {scores['scarcity']:.2f}",
            f"质量置信: {scores['quality']:.2f}",
            f"综合评分: {overall:.2f}"
        ]
        
        # 生成标签
        tags = self._extract_tags(content)
        
        return DensityScore(
            density_score=scores["density"],
            structure_score=scores["structure"],
            scarcity_score=scores["scarcity"],
            quality_score=scores["quality"],
            overall_score=overall,
            should_store=should_store,
            reason="; ".join(reason_parts),
            suggested_tags=tags
        )
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        """解析LLM响应"""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # 尝试提取JSON
            import re
            
            # 查找JSON代码块
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except:
                    pass
            
            # 查找花括号
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except:
                    pass
            
            # 默认值
            return {
                "density_score": 0.5,
                "structure_score": 0.5,
                "scarcity_score": 0.5,
                "quality_score": 0.5,
                "overall_score": 0.5,
                "should_store": False,
                "reason": "解析失败，使用默认值",
                "suggested_tags": []
            }
    
    def _extract_tags(self, content: str) -> List[str]:
        """从内容提取标签"""
        tags = []
        
        # 算法类型标签
        algo_types = {
            '动态规划': 'dp',
            '贪心': 'greedy',
            '回溯': 'backtrack',
            '分治': 'divide-conquer',
            '二分': 'binary-search',
            'DFS': 'dfs',
            'BFS': 'bfs',
            '递归': 'recursion',
            '迭代': 'iteration'
        }
        
        for cn, tag in algo_types.items():
            if cn in content:
                tags.append(tag)
        
        # 数据结构标签
        ds_types = {
            '数组': 'array',
            '链表': 'linked-list',
            '树': 'tree',
            '图': 'graph',
            '栈': 'stack',
            '队列': 'queue',
            '哈希': 'hashmap',
            '堆': 'heap'
        }
        
        for cn, tag in ds_types.items():
            if cn in content:
                tags.append(tag)
        
        # 难度标签
        if re.search(r'困难|困难|Hard', content):
            tags.append('hard')
        elif re.search(r'中等|Medium', content):
            tags.append('medium')
        elif re.search(r'简单|Easy', content):
            tags.append('easy')
        
        return list(set(tags))[:5]  # 最多5个标签


# 便捷函数
async def evaluate_content_density(
    content: str,
    llm=None,
    **kwargs
) -> DensityScore:
    """
    便捷的内容密度评估函数
    
    Args:
        content: 待评估内容
        llm: 大语言模型 (可选)
        **kwargs: 其他参数
        
    Returns:
        密度评分
    """
    checker = DensityChecker(llm, **kwargs)
    return await checker.evaluate(content)
