#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author   : PR
# @Time     : 2026/3/16 15:59
# @File     : knowledge_base.py
# @Project  : AlgoMate
import hashlib
import os.path
from datetime import datetime

from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

import config.config_data as config


def check_md5(md5_str: str) -> bool:
    """
    检查传入的md5字符串是否已经处理

    :param md5_str: md5字符串
    :return: 该md5是否已经被导入
    """
    if not os.path.exists(config.md5_path):
        open(config.md5_path, 'w', encoding='utf-8').close()    # 初始化md5文件
        return False

    with open(config.md5_path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            line = line.strip()
            if line == md5_str:
                return True

    return False

def save_md5(md5_str: str) -> None:
    """
    将传入的md5字符串持久化存储到文件

    :param md5_str:  md5字符串
    """
    with open(config.md5_path, 'a', encoding='utf-8') as f:
        f.write(md5_str + '\n')

def get_string_md5(input_str: str, encoding='utf-8') -> str:
    """
    将传入的文件转换为md5字符串

    :param input_str: 待编码的文件内容
    :param encoding: 文件编码格式
    :return: md5字符串
    """
    bytes = input_str.encode(encoding=encoding)
    md5 = hashlib.md5()
    md5.update(bytes)

    hex = md5.hexdigest()
    return hex

class KnowledgeBaseService(object):
    def __init__(self):
        # Chroma数据库
        os.makedirs(config.persist_directory, exist_ok=True)
        self.chroma = Chroma(
            collection_name=config.collection_name,
            embedding_function=DashScopeEmbeddings(model="text-embedding-v4"),
            persist_directory=config.persist_directory
        )

        # 文本分割器
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=config.separators,
            length_function=len
        )

    def upload_by_str(self, data:str, filename):
        """
        将传入的数据向量化，存入向量数据库中

        :param data: 待向量化数据
        :param filename: 数据对应文件的文件名
        """
        hex = get_string_md5(data)
        if check_md5(hex):
            return "[跳过]数据已在知识库中"

        if len(data) > config.max_split_char_number:
            knowledge = self.spliter.split_text(data)
        else:
            knowledge = [data]

        metadata = {
            "source": filename,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.chroma.add_texts(knowledge, metadatas=[metadata for _ in knowledge])
        save_md5(hex)

        return "[成功]内容已经成功载入向量库"
