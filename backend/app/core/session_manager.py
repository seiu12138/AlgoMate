"""
Session Manager for conversation persistence.
Handles CRUD operations for chat sessions with file-based storage.
"""
import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4
from pathlib import Path


class SessionManager:
    """Manages conversation sessions with file-based persistence."""
    
    def __init__(self, base_path: str = "data/chat_history"):
        """
        初始化会话管理器

        Args:
            base_path: 会话数据存储路径，默认 "data/chat_history"
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Ensure subdirectories exist
        (self.base_path / "rag").mkdir(exist_ok=True)
        (self.base_path / "agent").mkdir(exist_ok=True)
    
    def _get_session_path(self, session_id: str, session_type: str) -> Path:
        """
        获取会话文件路径

        Args:
            session_id: 会话唯一标识
            session_type: 会话类型（rag 或 agent）

        Returns:
            会话文件的 Path 对象
        """
        return self.base_path / session_type / f"session_{session_id}.json"
    
    def _get_index_path(self) -> Path:
        """
        获取会话索引文件路径

        Returns:
            索引文件的 Path 对象
        """
        return self.base_path / "sessions.json"
    
    def _load_index(self) -> List[Dict[str, Any]]:
        """
        加载会话索引

        Returns:
            会话元数据列表，空文件返回空列表
        """
        index_path = self._get_index_path()
        if not index_path.exists():
            return []
        with open(index_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_index(self, sessions: List[Dict[str, Any]]):
        """
        保存会话索引

        Args:
            sessions: 会话元数据列表
        """
        with open(self._get_index_path(), 'w', encoding='utf-8') as f:
            json.dump(sessions, f, ensure_ascii=False, indent=2)
    
    def create_session(self, session_type: str, title: str = None) -> Dict[str, Any]:
        """
        创建新会话

        Args:
            session_type: 会话类型（"rag" 或 "agent"）
            title: 会话标题，默认为 "New Conversation"

        Returns:
            新创建的会话元数据
        """
        session_id = str(uuid4())
        now = datetime.now().isoformat()
        
        session = {
            "id": session_id,
            "type": session_type,
            "title": title or "New Conversation",
            "createdAt": now,
            "updatedAt": now,
            "messageCount": 0,
            "lastMessagePreview": ""
        }
        
        # Save session file
        session_path = self._get_session_path(session_id, session_type)
        with open(session_path, 'w', encoding='utf-8') as f:
            json.dump({
                "session": session,
                "messages": []
            }, f, ensure_ascii=False, indent=2)
        
        # Update index
        index = self._load_index()
        index.append(session)
        self._save_index(index)
        
        return session
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定会话（包含消息）

        Args:
            session_id: 会话唯一标识

        Returns:
            包含会话元数据和消息的完整会话信息，不存在返回 None
        """
        # Find in index
        index = self._load_index()
        session_meta = next((s for s in index if s["id"] == session_id), None)
        if not session_meta:
            return None
        
        # Load full session
        session_path = self._get_session_path(session_id, session_meta["type"])
        if not session_path.exists():
            return None
        
        with open(session_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def add_message(self, session_id: str, message: Dict[str, Any]):
        """
        向会话添加消息

        Args:
            session_id: 会话唯一标识
            message: 消息对象（包含 role 和 content）

        Raises:
            ValueError: 会话不存在时抛出
        """
        session_data = self.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session {session_id} not found")
        
        # Add message
        message["id"] = str(uuid4())
        message["timestamp"] = datetime.now().isoformat()
        session_data["messages"].append(message)
        
        # Update session metadata
        session = session_data["session"]
        session["messageCount"] = len(session_data["messages"])
        session["updatedAt"] = datetime.now().isoformat()
        session["lastMessagePreview"] = message["content"][:50] + "..." if len(message["content"]) > 50 else message["content"]
        
        # Save session
        session_path = self._get_session_path(session_id, session["type"])
        with open(session_path, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        
        # Update index
        index = self._load_index()
        for i, s in enumerate(index):
            if s["id"] == session_id:
                index[i] = session
                break
        self._save_index(index)
    
    def list_sessions(self, session_type: str = None) -> List[Dict[str, Any]]:
        """
        获取所有会话列表

        Args:
            session_type: 可选，按类型过滤（"rag" 或 "agent"）

        Returns:
            按更新时间倒序排列的会话元数据列表
        """
        index = self._load_index()
        if session_type:
            index = [s for s in index if s["type"] == session_type]
        # Sort by updatedAt descending
        return sorted(index, key=lambda x: x["updatedAt"], reverse=True)
    
    def delete_session(self, session_id: str):
        """
        删除会话

        Args:
            session_id: 会话唯一标识
        """
        index = self._load_index()
        session_meta = next((s for s in index if s["id"] == session_id), None)
        if not session_meta:
            return
        
        # Delete file
        session_path = self._get_session_path(session_id, session_meta["type"])
        if session_path.exists():
            session_path.unlink()
        
        # Update index
        index = [s for s in index if s["id"] != session_id]
        self._save_index(index)
    
    def update_title(self, session_id: str, title: str):
        """
        更新会话标题

        Args:
            session_id: 会话唯一标识
            title: 新标题
        """
        index = self._load_index()
        for s in index:
            if s["id"] == session_id:
                s["title"] = title
                s["updatedAt"] = datetime.now().isoformat()
                break
        self._save_index(index)
        
        # Also update in session file
        session_data = self.get_session(session_id)
        if session_data:
            session_data["session"]["title"] = title
            session_data["session"]["updatedAt"] = datetime.now().isoformat()
            session_path = self._get_session_path(session_id, session_data["session"]["type"])
            with open(session_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)


# Global instance for dependency injection
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """
    获取全局 SessionManager 实例

    Returns:
        SessionManager 单例实例
    """
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
