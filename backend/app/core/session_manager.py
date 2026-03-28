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
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Ensure subdirectories exist
        (self.base_path / "rag").mkdir(exist_ok=True)
        (self.base_path / "agent").mkdir(exist_ok=True)
    
    def _get_session_path(self, session_id: str, session_type: str) -> Path:
        return self.base_path / session_type / f"session_{session_id}.json"
    
    def _get_index_path(self) -> Path:
        return self.base_path / "sessions.json"
    
    def _load_index(self) -> List[Dict[str, Any]]:
        index_path = self._get_index_path()
        if not index_path.exists():
            return []
        with open(index_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_index(self, sessions: List[Dict[str, Any]]):
        with open(self._get_index_path(), 'w', encoding='utf-8') as f:
            json.dump(sessions, f, ensure_ascii=False, indent=2)
    
    def create_session(self, session_type: str, title: str = None) -> Dict[str, Any]:
        """Create a new session"""
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
        """Load a specific session with messages"""
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
        """Add message to session"""
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
        """List all sessions, optionally filtered by type"""
        index = self._load_index()
        if session_type:
            index = [s for s in index if s["type"] == session_type]
        # Sort by updatedAt descending
        return sorted(index, key=lambda x: x["updatedAt"], reverse=True)
    
    def delete_session(self, session_id: str):
        """Delete a session"""
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
        """Update session title"""
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
    """Get or create global SessionManager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
