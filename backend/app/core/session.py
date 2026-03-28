#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
会话管理模块
使用内存字典存储会话状态
"""
import os
import sys
from typing import Dict, Any

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.rag import RagService
from agent.react_agent import AlgoMateAgent


class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        获取会话，如果不存在则创建新会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话数据字典
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "messages": [],
                "rag": RagService(),
                "agent": None,
                "agent_results": {}
            }
        return self.sessions[session_id]
    
    def clear_session(self, session_id: str) -> bool:
        """
        清空会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否成功清空
        """
        if session_id in self.sessions:
            # 清理 RAG 历史
            try:
                rag_service = self.sessions[session_id].get("rag")
                if rag_service:
                    # 重置 RAG 会话历史
                    from rag.file_history_store import get_history
                    history = get_history(session_id)
                    history.clear()
            except Exception as e:
                print(f"清理 RAG 历史失败: {e}")
            
            # 删除会话
            del self.sessions[session_id]
            return True
        return False
    
    def get_or_create_agent(self, session_id: str, max_iterations: int = 5) -> AlgoMateAgent:
        """
        获取或创建 Agent 实例
        
        Args:
            session_id: 会话ID
            max_iterations: 最大迭代次数
            
        Returns:
            Agent 实例
        """
        session = self.get_session(session_id)
        
        # 如果 agent 不存在或配置不同，则创建新的
        if session.get("agent") is None:
            session["agent"] = AlgoMateAgent(max_iterations=max_iterations)
        
        return session["agent"]


# 全局会话管理器实例
session_manager = SessionManager()


# 便捷函数
def get_session(session_id: str) -> Dict[str, Any]:
    """获取会话"""
    return session_manager.get_session(session_id)


def clear_session(session_id: str) -> bool:
    """清空会话"""
    return session_manager.clear_session(session_id)


def get_or_create_agent(session_id: str, max_iterations: int = 5) -> AlgoMateAgent:
    """获取或创建 Agent"""
    return session_manager.get_or_create_agent(session_id, max_iterations)
