#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author   : PR
# @Time     : 2026/3/16 16:35
# @File     : rag.py
# @Project  : AlgoMate
from typing import List

from langchain_community.chat_models import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from utils.prompts_loader import (
    load_rag_system_role_prompt,
    load_rag_context_prompt,
    load_rag_history_prompt,
    load_rag_user_prompt,
)
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory, RunnableLambda

from .file_history_store import get_history
from .vector_stores import VectorStoreService

from utils.config_handler import model_conf


class RagService(object):
    def __init__(self):
        self.vector_service = VectorStoreService(embedding=DashScopeEmbeddings(model=model_conf['embedding_model_name']))
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", load_rag_system_role_prompt()),
            ("system", load_rag_context_prompt()),
            ("system", load_rag_history_prompt()),
            MessagesPlaceholder("history"),
            ("user", load_rag_user_prompt())
        ])
        self.chat_model = ChatTongyi(model=model_conf['chat_model_name'])
        self.chain = self.__get_chain()

    def __get_chain(self):
        retriever = self.vector_service.get_retriever()

        def __format_document(docs: List[Document]) -> str:
            if not docs:
                return "无相关参考资料"

            formatted_str = ""
            for doc in docs:
                formatted_str += f"资料片段: {doc.page_content}\n资料元数据: {doc.metadata}\n\n"
            return formatted_str

        def __format_history_input(value: dict) -> str:
            return value["input"]

        def __format_prompt_input(value: dict) -> dict:
            format_input = {}
            format_input["input"] = value["input"]["input"]
            format_input["history"] = value["input"]["history"]
            format_input["context"] = value["context"]
            return format_input

        chain = {"input": RunnablePassthrough(),
                 "context": RunnableLambda(__format_history_input) | retriever | __format_document
                 } | RunnableLambda(__format_prompt_input) | self.prompt_template | self.chat_model | StrOutputParser()

        conversion_chain = RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history"
        )

        return conversion_chain
