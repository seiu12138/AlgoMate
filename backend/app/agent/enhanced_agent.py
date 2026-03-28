#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Enhanced Agent with RAG integration and session persistence.
Wraps the existing AlgoMateAgent with conversation management capabilities.
"""
from typing import Dict, Any, Optional
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate

from app.core.session_manager import get_session_manager
from .react_agent import AlgoMateAgent


class EnhancedAgent:
    """
    Enhanced Agent with RAG retrieval and session persistence.
    
    Features:
    - Stores all messages in session storage
    - Retrieves relevant context from vector DB for problem solving
    - Auto-generates conversation titles
    """
    
    def __init__(self, llm, session_manager=None, conversation_rag=None, max_iterations: int = 5):
        """
        初始化增强型 Agent

        Args:
            llm: 大语言模型实例
            session_manager: 会话管理器实例，默认使用全局实例
            conversation_rag: RAG 服务实例，可选
            max_iterations: 最大迭代次数，默认 5
        """
        self.llm = llm
        self.session_manager = session_manager or get_session_manager()
        self.conversation_rag = conversation_rag
        self.max_iterations = max_iterations
        
        # Initialize the underlying React Agent
        self.react_agent = AlgoMateAgent(llm=llm, max_iterations=max_iterations)
        
        # Prompt for generating agent conversation titles
        self.summary_prompt = ChatPromptTemplate.from_messages([
            ("system", """Based on this programming problem, generate a concise 3-5 word title.
Focus on the algorithm or problem type.

Respond with ONLY the title."""),
            ("user", "Problem: {problem}")
        ])
    
    async def process(
        self,
        problem_description: str,
        session_id: str,
        language: str = "python"
    ) -> Dict[str, Any]:
        """
        处理编程题目（同步模式）

        Args:
            problem_description: 题目描述
            session_id: 会话ID（用于持久化）
            language: 编程语言（python/cpp/java），默认 python

        Returns:
            Agent 执行结果字典，包含 final_answer、generated_code、is_solved 等
        """
        # 1. Store user message
        self.session_manager.add_message(session_id, {
            "role": "user",
            "content": problem_description
        })
        
        # 2. Get RAG-enhanced context if available
        enhanced_context = ""
        if self.conversation_rag:
            try:
                enhanced_context = await self.conversation_rag.get_enhanced_context(
                    query=problem_description,
                    session_id=session_id,
                    k=3,
                    max_history=5
                )
            except Exception as e:
                print(f"Warning: Failed to get RAG context: {e}")
        
        # 3. Enhance problem with context
        if enhanced_context:
            enhanced_problem = f"""{problem_description}

[Additional Context from Knowledge Base]
{enhanced_context}
"""
        else:
            enhanced_problem = problem_description
        
        # 4. Process with React Agent
        result = self.react_agent.solve(
            problem=enhanced_problem,
            language=language,
            session_id=session_id
        )
        
        # 5. Extract result fields
        final_answer = result.get("final_answer", "")
        generated_code = result.get("generated_code", "")
        is_solved = result.get("is_solved", False)
        execution_history = result.get("execution_history", [])
        iteration_count = result.get("iteration_count", 0)
        
        # 6. Store assistant response with metadata
        self.session_manager.add_message(session_id, {
            "role": "assistant",
            "content": final_answer,
            "metadata": {
                "generatedCode": generated_code,
                "executionResult": execution_history[-1] if execution_history else None,
                "isSolved": is_solved,
                "iterationCount": iteration_count,
                "language": language
            }
        })
        
        # 7. Auto-generate title if first message
        session_data = self.session_manager.get_session(session_id)
        if session_data and session_data["session"]["messageCount"] <= 2:
            try:
                title = await self._generate_summary(problem_description)
                self.session_manager.update_title(session_id, title)
            except Exception as e:
                print(f"Warning: Failed to generate title: {e}")
        
        # 8. Also store solution in vector DB if solved and RAG available
        if is_solved and self.conversation_rag and final_answer:
            try:
                await self.conversation_rag.process_message(
                    session_id=session_id,
                    message=final_answer,
                    role="assistant"
                )
            except Exception as e:
                print(f"Warning: Failed to store solution in vector DB: {e}")
        
        return {
            "final_answer": final_answer,
            "generated_code": generated_code,
            "is_solved": is_solved,
            "execution_history": execution_history,
            "iteration_count": iteration_count,
            "language": language
        }
    
    async def process_stream(
        self,
        problem_description: str,
        session_id: str,
        language: str = "python"
    ):
        """
        处理编程题目（流式模式）

        Args:
            problem_description: 题目描述
            session_id: 会话ID（用于持久化）
            language: 编程语言（python/cpp/java），默认 python

        Yields:
            处理过程中的事件字典
        """
        # 1. Store user message
        self.session_manager.add_message(session_id, {
            "role": "user",
            "content": problem_description
        })
        
        # 2. Get RAG context
        enhanced_context = ""
        if self.conversation_rag:
            try:
                enhanced_context = await self.conversation_rag.get_enhanced_context(
                    query=problem_description,
                    session_id=session_id,
                    k=3,
                    max_history=5
                )
            except Exception as e:
                print(f"Warning: Failed to get RAG context: {e}")
        
        # 3. Enhance problem
        if enhanced_context:
            enhanced_problem = f"""{problem_description}

[Additional Context from Knowledge Base]
{enhanced_context}
"""
        else:
            enhanced_problem = problem_description
        
        # 4. Stream process with React Agent
        final_result = {}
        for event in self.react_agent.solve_stream(
            problem=enhanced_problem,
            language=language,
            session_id=session_id
        ):
            yield event
            
            # Capture final state from events
            for node_name, output in event.items():
                if node_name == "finish":
                    final_result = output
        
        # 5. Get final state
        thread_config = {"configurable": {"thread_id": session_id}}
        final_state = self.react_agent.graph.get_state(thread_config)
        
        if final_state:
            result = {
                "final_answer": final_state.values.get("final_answer", ""),
                "is_solved": final_state.values.get("is_solved", False),
                "generated_code": final_state.values.get("generated_code", ""),
                "language": final_state.values.get("language", language),
                "iteration_count": final_state.values.get("iteration_count", 0),
                "execution_history": final_state.values.get("execution_history", []),
            }
        else:
            result = {"error": "未能获取最终状态"}
        
        # 6. Store assistant response
        self.session_manager.add_message(session_id, {
            "role": "assistant",
            "content": result.get("final_answer", ""),
            "metadata": {
                "generatedCode": result.get("generated_code"),
                "executionResult": result.get("execution_history", [])[-1] if result.get("execution_history") else None,
                "isSolved": result.get("is_solved"),
                "iterationCount": result.get("iteration_count"),
                "language": language
            }
        })
        
        # 7. Auto-generate title
        session_data = self.session_manager.get_session(session_id)
        if session_data and session_data["session"]["messageCount"] <= 2:
            try:
                title = await self._generate_summary(problem_description)
                self.session_manager.update_title(session_id, title)
                yield {"__title_update__": {"title": title}}
            except Exception as e:
                print(f"Warning: Failed to generate title: {e}")
        
        yield result
    
    async def _generate_summary(self, problem: str) -> str:
        """
        生成会话标题

        Args:
            problem: 问题描述

        Returns:
            生成的标题
        """
        if not problem or len(problem.strip()) < 5:
            return "Coding Problem"
        
        try:
            chain = self.summary_prompt | self.llm
            response = await chain.ainvoke({"problem": problem[:500]})
            title = response.content.strip()[:50]
            return title or "Coding Problem"
        except Exception:
            # Fallback
            return problem[:30] + "..." if len(problem) > 30 else problem


# Global instance
_enhanced_agent: Optional[EnhancedAgent] = None


def get_enhanced_agent(llm=None, session_manager=None, conversation_rag=None) -> EnhancedAgent:
    """
    获取全局 EnhancedAgent 实例

    Args:
        llm: 大语言模型实例（首次初始化必需）
        session_manager: 会话管理器实例，可选
        conversation_rag: RAG 服务实例，可选

    Returns:
        EnhancedAgent 单例实例

    Raises:
        ValueError: 首次初始化时缺少 llm 参数
    """
    global _enhanced_agent
    if _enhanced_agent is None:
        if llm is None:
            raise ValueError("llm is required for first initialization")
        _enhanced_agent = EnhancedAgent(llm, session_manager, conversation_rag)
    return _enhanced_agent
