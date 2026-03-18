#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author   : PR
# @Time     : 2026/3/16 16:46
# @File     : file_history_store.py
# @Project  : AlgoMate
import json
import os
from json import JSONDecodeError
from typing import Sequence, List

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict
import config.config_data as config


class FileChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id, storage_path):
        self.session_id = session_id
        self.storage_path = storage_path

        self.file_path = os.path.join(self.storage_path, self.session_id)
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        all_messages = list(self.messages)
        all_messages.extend(messages)

        new_messages = [message_to_dict(message) for message in all_messages]
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(new_messages, f)

    @property
    def messages(self) -> List[BaseMessage]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return messages_from_dict(json.load(f))
        except Exception:
            return []

    def clear(self) -> None:
        with open(self.file_path, "r", encoding="utf-8") as f:
            json.dump([], f)

def get_history(session_id):
    return FileChatMessageHistory(session_id, config.history_path)