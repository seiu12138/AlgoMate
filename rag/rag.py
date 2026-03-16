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
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory, RunnableLambda

from .file_history_store import get_history
from .vector_stores import VectorStoreService

import config.config_data as config


class RagService(object):
    def __init__(self):
        self.vector_service = VectorStoreService(embedding=DashScopeEmbeddings(model=config.embedding_model_name))
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "考虑你是一个对于精通计算机算法的编程人员，请以此身份回答一下问题。"),
            ("system", "我将为你提供用户提问相关资料: {context}。"),
            ("system", "我将为你提供用户历史提问信息如下："),
            MessagesPlaceholder("history"),
            ("user", "基于上述内容解答用户所询问的题目，并且给出核心思路的分析。请回答用户待求解的题目: {input}")
        ])
        self.chat_model = ChatTongyi(model=config.chat_model_name)
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
