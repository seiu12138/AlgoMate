#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author   : PR
# @Time     : 2026/3/16 16:31
# @File     : vector_stores.py
# @Project  : AlgoMate
import os
from typing import List

from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from utils.config_handler import chroma_conf, search_conf, splitter_conf, storage_conf
from utils.file_handler import (
    get_file_md5_hex,
    listdir_with_allowed_type,
    pdf_loader,
    text_loader,
)
from utils.logger_handler import log_flow
from utils.path_tool import get_abs_path


class VectorStoreService(object):
    """向量存储服务"""

    def __init__(self, embedding):
        """
        初始化向量存储服务

        Args:
            embedding: 嵌入模型实例
        """
        self.embedding = embedding
        self.vector_store = Chroma(
            collection_name=chroma_conf['collection_name'],
            embedding_function=self.embedding,
            persist_directory=get_abs_path(chroma_conf['persist_directory'])
        )

        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=splitter_conf["chunk_size"],
            chunk_overlap=splitter_conf["chunk_overlap"],
            separators=splitter_conf["separators"],
            length_function=len
        )

    def get_retriever(self):
        """
        获取检索器

        Returns:
            Chroma检索器实例
        """
        return self.vector_store.as_retriever(search_kwargs={"k": search_conf['max_search_key']})

    def _check_md5_hex(self, md5_for_check: str) -> bool:
        """
        检查MD5是否已存在于记录中

        Args:
            md5_for_check: 待检查的MD5值

        Returns:
            True表示已存在，False表示不存在
        """
        md5_path = get_abs_path(storage_conf["md5_path"])
        if not os.path.exists(md5_path):
            open(md5_path, "w", encoding="utf-8").close()
            return False

        with open(md5_path, "r", encoding='utf-8') as f:
            for line in f.readlines():
                if line.strip() == md5_for_check:
                    return True
        return False

    def _save_md5(self, md5: str) -> None:
        """
        保存MD5值到记录文件

        Args:
            md5: MD5值
        """
        md5_path = get_abs_path(storage_conf["md5_path"])
        with open(md5_path, "a", encoding='utf-8') as f:
            f.write(md5 + "\n")

    def _get_file_documents(self, read_path: str, passwd: str = None) -> List[Document]:
        """
        根据文件类型加载文档

        Args:
            read_path: 文件路径
            passwd: PDF文件密码（可选）

        Returns:
            Document列表
        """
        if read_path.endswith(".txt"):
            return text_loader(read_path)
        elif read_path.endswith(".pdf"):
            return pdf_loader(read_path, passwd)
        else:
            return []

    def load_document(self) -> int:
        """
        加载文件到Chroma知识库

        扫描配置的数据目录，将允许类型的文件加载到向量数据库中，
        使用MD5去重避免重复加载。

        Returns:
            新加载的文档片段数量
        """
        import os

        allowed_files_path = listdir_with_allowed_type(
            get_abs_path(chroma_conf["data_path"]),
            tuple(chroma_conf["allow_knowledge_file_type"])
        )

        total_chunks = 0
        for path in allowed_files_path:
            md5 = get_file_md5_hex(path)
            if not md5:
                continue

            if self._check_md5_hex(md5):
                log_flow("KnowledgeBase", f"[加载知识库]: {path}已存在于知识库中")
                continue

            try:
                documents: List[Document] = self._get_file_documents(path)
                if not documents:
                    log_flow("KnowledgeBase", f"[加载知识库]: {path}没有有效文本内容", level=30)
                    continue

                split_documents = self.spliter.split_documents(documents)
                if not split_documents:
                    log_flow("KnowledgeBase", f"[加载知识库]: {path}分片后没有有效文本内容", level=30)
                    continue

                self.vector_store.add_documents(split_documents)
                self._save_md5(md5)
                total_chunks += len(split_documents)
                log_flow("KnowledgeBase", f"[加载知识库]: {path}加载成功，生成 {len(split_documents)} 个文档片段")
            except Exception as e:
                log_flow("KnowledgeBase", f"[加载知识库]: {path}加载失败, {str(e)}", level=40)

        return total_chunks

    def add_texts(self, texts: List[str], metadatas: List[dict] = None) -> None:
        """
        将文本添加到向量数据库

        Args:
            texts: 文本列表
            metadatas: 元数据列表
        """
        self.vector_store.add_texts(texts, metadatas)

    def similarity_search_with_score(self, query: str, k: int = 3) -> List[tuple]:
        """
        相似度搜索并返回分数

        Args:
            query: 查询文本
            k: 返回结果数量

        Returns:
            (文档, 分数) 元组列表
        """
        return self.vector_store.similarity_search_with_score(query, k=k)

    def test_retrieval(self, query: str = "动态规划", top_k: int = 3) -> None:
        """
        测试知识库检索功能

        执行检索测试并输出结果，用于验证预热后的知识库是否正常工作。

        Args:
            query: 测试查询语句，默认为"动态规划"
            top_k: 返回的最大结果数，默认为3

        Example:
            >>> service = VectorStoreService(embedding)
            >>> service.load_document()  # 预热
            >>> service.test_retrieval("二分查找")  # 测试检索
        """
        from langchain_core.documents import Document

        log_flow("KnowledgeBase", f"[检索测试]: 查询='{query}', top_k={top_k}")

        try:
            retriever = self.get_retriever()
            docs: List[Document] = retriever.invoke(query)

            if not docs:
                log_flow("KnowledgeBase", "[检索测试]: 未找到相关文档", level=30)
                return

            log_flow("KnowledgeBase", f"[检索测试]: 找到 {len(docs)} 个相关片段")
            print("\n" + "=" * 60)
            print(f"检索查询: {query}")
            print("=" * 60)

            for i, doc in enumerate(docs[:top_k], 1):
                print(f"\n[结果 {i}]")
                print(f"来源: {doc.metadata.get('source', 'Unknown')}")
                print(f"页码: {doc.metadata.get('page', 'N/A')}")
                print(f"内容预览: {doc.page_content[:200]}...")
                print("-" * 60)

        except Exception as e:
            log_flow("KnowledgeBase", f"[检索测试]: 检索失败 - {str(e)}", level=40)


if __name__ == "__main__":
    retriever = VectorStoreService(embedding=DashScopeEmbeddings(model="text-embedding-v2")).test_retrieval("binary_search")
