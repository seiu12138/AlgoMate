#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author   : PR
# @Time     : 2026/3/16
# @File     : react_agent.py
# @Project  : AlgoMate
from typing import Dict, Any, Iterator
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.chat_models import ChatTongyi

from .state import AgentState, create_initial_state
from .nodes import AgentNodes
import config.config_data as config
from utils.logger_handler import log_agent



class AlgoMateAgent:
    """
    AlgoMate ReAct Agent实现
    """
    
    def __init__(self, llm=None, max_iterations: int = 5):
        """
        初始化Agent

        Args:
            llm: LangChain语言模型，默认使用配置中的模型
            max_iterations: 最大代码修复迭代次数
        """
        # 初始化语言模型
        if llm is None:
            self.llm = ChatTongyi(model=config.chat_model_name)
        else:
            self.llm = llm
        
        self.max_iterations = max_iterations
        self.nodes = AgentNodes(self.llm)
        
        # 构建工作流图
        self.graph = self._build_graph()
        
        log_agent(f"AlgoMateAgent初始化完成，最大迭代次数: {max_iterations}")
    
    def _build_graph(self) -> StateGraph:
        """
        构建LangGraph工作流

        Returns:
            编译后的StateGraph
        """
        # 创建工作流
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("analyze", self.nodes.analyze_problem)
        workflow.add_node("generate_test_cases", self.nodes.generate_test_cases)
        workflow.add_node("generate_code", self.nodes.generate_code)
        workflow.add_node("execute_code", self.nodes.execute_code)
        workflow.add_node("analyze_result", self.nodes.analyze_result)
        workflow.add_node("fix_code", self.nodes.fix_code)
        workflow.add_node("finish", self.nodes.create_final_answer)
        
        # 设置入口点
        workflow.set_entry_point("analyze")
        
        # 添加边
        workflow.add_edge("analyze", "generate_test_cases")
        workflow.add_edge("generate_test_cases", "generate_code")
        workflow.add_edge("generate_code", "execute_code")
        workflow.add_edge("execute_code", "analyze_result")
        
        # 条件边：根据分析结果决定下一步
        workflow.add_conditional_edges(
            "analyze_result",
            self._should_continue,
            {
                "fix": "fix_code",
                "reexecute": "execute_code",  # 测试用例修正后重新执行
                "finish": "finish"
            }
        )
        
        # 修复后循环回执行
        workflow.add_edge("fix_code", "execute_code")
        
        # 结束
        workflow.add_edge("finish", END)
        
        # 编译，添加内存检查点（支持流式输出）
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)
    
    def _should_continue(self, state: AgentState) -> str:
        """
        决定是否继续迭代

        Args:
            state: 当前Agent状态

        Returns:
            "fix"修复代码 / "reexecute"重新执行 / "finish"结束
        """
        if state.get("is_solved", False):
            return "finish"
        
        if state.get("iteration_count", 0) >= state.get("max_iterations", 5):
            return "finish"
        
        # 检查是否是重新执行（测试用例已修正）
        next_step = state.get("next_step", "")
        if next_step == "execute_code":
            return "reexecute"
        
        return "fix"
    
    def solve(self, problem_description: str, 
              language: str = "python",
              session_id: str = "default") -> Dict[str, Any]:
        """
        解决算法问题（同步模式）
        
        Args:
            problem_description: 题目描述
            language: 编程语言（python/cpp/java）
            session_id: 会话ID，用于持久化
        
        Returns:
            包含 final_answer 的字典
        
        Example:
            >>> agent = AlgoMateAgent()
            >>> result = agent.solve("两数之和问题...")
            >>> print(result["final_answer"])
        """
        # 创建初始状态
        initial_state = create_initial_state(
            problem_description=problem_description,
            language=language,
            max_iterations=self.max_iterations
        )
        
        # 配置
        thread_config = {
            "configurable": {
                "thread_id": session_id
            }
        }
        
        # 执行
        log_agent("=" * 60)
        log_agent("开始解决问题")
        log_agent("=" * 60)
        log_agent(f"题目: {problem_description[:100]}...")
        log_agent(f"编程语言: {language}")
        
        final_state = None
        for event in self.graph.stream(initial_state, thread_config):
            # event 是字典，key 是节点名，value 是输出
            for node_name, output in event.items():
                if node_name == "__end__":
                    continue
                log_agent(f"节点 '{node_name}' 完成")
        
        # 获取最终状态
        final_state = self.graph.get_state(thread_config)
        
        log_agent("=" * 60)
        log_agent("问题解决流程结束")
        log_agent("=" * 60)
        
        return final_state.values if final_state else {}
    
    def solve_stream(self, problem_description: str,
                     language: str = "python",
                     session_id: str = "default") -> Iterator[Dict[str, Any]]:
        """
        解决算法问题（流式模式）
        
        实时产生中间结果，适合 Web 界面展示。
        
        Args:
            problem_description: 题目描述
            language: 编程语言
            session_id: 会话ID
        
        Yields:
            每个节点的输出状态
        
        Example:
            >>> for state in agent.solve_stream("问题..."):
            ...     print(state.get("next_step"))
        """
        initial_state = create_initial_state(
            problem_description=problem_description,
            language=language,
            max_iterations=self.max_iterations
        )
        
        thread_config = {
            "configurable": {
                "thread_id": session_id
            }
        }
        
        for event in self.graph.stream(initial_state, thread_config):
            yield event
    
    def get_execution_trace(self, session_id: str = "default") -> list:
        """
        获取执行轨迹

        Args:
            session_id: 会话ID，用于调试和展示

        Returns:
            执行历史列表
        """
        thread_config = {
            "configurable": {
                "thread_id": session_id
            }
        }
        
        state = self.graph.get_state(thread_config)
        if state:
            return state.values.get("execution_history", [])
        return []


# ============ 便捷函数 ============
def solve_problem(problem_description: str, 
                  language: str = "python",
                  max_iterations: int = 5) -> str:
    """
    便捷函数：快速解决算法问题

    Args:
        problem_description: 题目描述
        language: 编程语言（python/cpp/java）
        max_iterations: 最大迭代次数

    Returns:
        最终答案字符串

    Example:
        >>> answer = solve_problem("两数之和: 给定数组 nums 和 target...")
        >>> print(answer)
    """
    agent = AlgoMateAgent(max_iterations=max_iterations)
    result = agent.solve(problem_description, language)
    return result.get("final_answer", "未能生成答案")


# ============ 测试代码 ============

if __name__ == "__main__":
    # 测试 Agent
    
    test_problem = """
题目：两数之和

给定一个整数数组 nums 和一个整数目标值 target，请你在该数组中找出和为目标值 target 的那两个整数，并返回它们的数组下标。

你可以假设每种输入只会对应一个答案。但是，数组中同一个元素在答案里不能重复出现。

你可以按任意顺序返回答案。

示例 1：
输入：nums = [2,7,11,15], target = 9
输出：[0,1]
解释：因为 nums[0] + nums[1] == 9 ，返回 [0, 1] 。

示例 2：
输入：nums = [3,2,4], target = 6
输出：[1,2]

示例 3：
输入：nums = [3,3], target = 6
输出：[0,1]
"""
    
    print("="*80)
    print("测试 AlgoMate ReAct Agent")
    print("="*80)
    
    try:
        agent = AlgoMateAgent(max_iterations=3)
        result = agent.solve(test_problem, language="python")
        
        print("\n" + "="*80)
        print("最终结果:")
        print("="*80)
        print(result.get("final_answer", "无结果"))
        
        # 打印执行历史
        history = result.get("execution_history", [])
        print(f"\n执行历史 ({len(history)} 次尝试):")
        for h in history:
            print(f"  尝试 {h['iteration']}: {h['result'].get('error_type', '成功')}")
    
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
