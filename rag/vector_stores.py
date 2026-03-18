#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author   : PR
# @Time     : 2026/3/16 16:31
# @File     : vector_stores.py
# @Project  : AlgoMate
from langchain_chroma import Chroma
from utils.config_handler import chroma_conf, search_conf

class VectorStoreService(object):
    def __init__(self, embedding):
        self.embedding = embedding
        self.vector_store = Chroma(
            collection_name=chroma_conf['collection_name'],
            embedding_function=self.embedding,
            persist_directory=chroma_conf['persist_directory']
        )

    def get_retriever(self):
        return self.vector_store.as_retriever(searck_kwargs={"k": search_conf['max_search_key']})