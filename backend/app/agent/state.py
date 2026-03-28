#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author   : PR
# @Time     : 2026/3/16
# @File     : state.py
# @Project  : AlgoMate
from typing import Annotated, List, Optional, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
import operator


class TestCase(TypedDict):
    """测试用例定义"""
    input: str
    expected: str
    actual: Optional[str]
    passed: Optional[bool]


class ExecutionHistory(TypedDict):
    """单次执行历史记录"""
    iteration: int
    code: str
    language: str
    result: dict  # ExecutionResult.to_dict()
    analysis: str  # AI 对结果的分析
    fixes: Optional[str]  # 计划修复的内容
    potential_test_case_error: Optional[bool]  # 是否怀疑测试用例错误


class AgentState(TypedDict):
    """
    ReAct Agent 完整状态
    
    字段说明：
    - messages: 对话历史（使用 operator.add 自动合并）
    - problem_description: 用户输入的题目描述
    - problem_analysis: AI 对题目的分析（输入、输出、约束等）
    - generated_code: 当前生成的代码
    - language: 编程语言
    - test_cases: 测试用例列表（自动生成或用户提供）
    - execution_result: 最后一次执行结果
    - execution_history: 所有执行尝试的历史记录
    - iteration_count: 当前迭代次数
    - max_iterations: 最大迭代次数
    - final_answer: 最终答案/解答
    - is_solved: 问题是否已解决
    - next_step: 下一步行动（'generate', 'execute', 'fix', 'finish'）
    """
    
    # 消息历史（LangChain 标准格式）
    messages: Annotated[List[BaseMessage], operator.add]
    
    # 题目相关信息
    problem_description: str
    problem_analysis: Optional[str]
    
    # 代码相关信息
    generated_code: Optional[str]
    language: Optional[str]
    
    # 测试相关
    test_cases: Optional[List[TestCase]]
    execution_result: Optional[dict]
    
    # 迭代控制
    execution_history: Annotated[List[ExecutionHistory], operator.add]
    iteration_count: int
    max_iterations: int
    
    # 结果
    final_answer: Optional[str]
    is_solved: bool
    next_step: str  # 'analyze', 'generate', 'execute', 'fix', 'finish'


def create_initial_state(problem_description: str, 
                        language: str = "python",
                        max_iterations: int = 5) -> AgentState:
    """
    创建初始状态

    Args:
        problem_description: 题目描述
        language: 目标编程语言
        max_iterations: 最大尝试次数

    Returns:
        初始化的AgentState
    """
    return AgentState(
        messages=[HumanMessage(content=problem_description)],
        problem_description=problem_description,
        problem_analysis=None,
        generated_code=None,
        language=language,
        test_cases=None,
        execution_result=None,
        execution_history=[],
        iteration_count=0,
        max_iterations=max_iterations,
        final_answer=None,
        is_solved=False,
        next_step="analyze"
    )
