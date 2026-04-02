#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File-based chat message history storage for LangChain.

This module provides a file-based implementation of BaseChatMessageHistory,
enabling persistent storage of conversation history across sessions.
"""
import json
import os
from json import JSONDecodeError
from typing import Sequence, List

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict
from utils.config_handler import storage_conf


class FileChatMessageHistory(BaseChatMessageHistory):
    """
    基于文件的聊天消息历史存储
    
    继承自 LangChain 的 BaseChatMessageHistory，提供文件持久化存储功能。
    每个会话的消息被存储为单独的 JSON 文件，便于管理和备份。
    
    Attributes:
        session_id: 会话唯一标识
        storage_path: 存储目录路径
        file_path: 会话文件完整路径
    
    Example:
        >>> history = FileChatMessageHistory("session_001", "/data/history")
        >>> history.add_messages([HumanMessage(content="Hello")])
        >>> messages = history.messages
    """
    
    def __init__(self, session_id: str, storage_path: str):
        """
        初始化文件消息历史存储
        
        Args:
            session_id: 会话唯一标识
            storage_path: 存储目录路径
        """
        self.session_id = session_id
        self.storage_path = storage_path

        self.file_path = os.path.join(self.storage_path, self.session_id)
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        """
        添加消息到历史记录
        
        将新消息追加到现有历史记录中，并保存到文件。
        
        Args:
            messages: 要添加的消息序列
        """
        all_messages = list(self.messages)
        all_messages.extend(messages)

        new_messages = [message_to_dict(message) for message in all_messages]
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(new_messages, f)

    @property
    def messages(self) -> List[BaseMessage]:
        """
        获取所有消息
        
        从文件中读取并反序列化所有消息。
        
        Returns:
            消息列表，文件不存在或解析失败时返回空列表
        """
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return messages_from_dict(json.load(f))
        except Exception:
            return []

    def clear(self) -> None:
        """
        清空消息历史
        
        将消息列表重置为空并保存到文件。
        """
        with open(self.file_path, "r", encoding="utf-8") as f:
            json.dump([], f)


def get_history(session_id: str) -> FileChatMessageHistory:
    """
    获取指定会话的历史存储实例
    
    便捷函数，用于根据 session_id 创建 FileChatMessageHistory 实例。
    存储路径从配置中读取。
    
    Args:
        session_id: 会话唯一标识
        
    Returns:
        FileChatMessageHistory 实例
        
    Example:
        >>> history = get_history("user_123")
        >>> history.add_messages([AIMessage(content="Hello!")])
    """
    return FileChatMessageHistory(session_id, storage_conf['history_path'])
