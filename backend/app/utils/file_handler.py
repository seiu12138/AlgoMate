#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author   : PR
# @Time     : 2026/3/18 15:38
# @File     : file_handler.py
# @Project  : AlgoMate
import hashlib
import os
from typing import List, Tuple

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document

from utils.logger_handler import log_flow
from utils.path_tool import get_abs_path

FILE_CHUNK_SIZE = 4096


def get_file_md5_hex(filepath: str) -> str:
    """
    计算文件的MD5哈希值

    Args:
        filepath: 文件路径

    Returns:
        MD5十六进制字符串，计算失败返回空字符串

    Example:
        >>> md5 = get_file_md5_hex("./data/test.txt")
        >>> print(md5)
        "d41d8cd98f00b204e9800998ecf8427e"
    """
    if not os.path.exists(filepath):
        log_flow("FileHandler", f"[md5计算]: 文件{filepath}不存在", level=40)
        return ""

    if not os.path.isfile(filepath):
        log_flow("FileHandler", f"[md5计算]: 路径{filepath}不是文件", level=40)
        return ""

    md5_obj = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(FILE_CHUNK_SIZE):
                md5_obj.update(chunk)

        return md5_obj.hexdigest()
    except Exception as e:
        log_flow("FileHandler", f"[md5计算]: 计算文件{filepath}md5失败，{str(e)}", level=40)
        return ""


def listdir_with_allowed_type(path: str, allowed_types: Tuple[str, ...]) -> Tuple[str, ...]:
    """
    返回文件夹内特定文件类型的文件列表

    Args:
        path: 文件夹路径
        allowed_types: 允许的文件类型元组，如(".txt", ".pdf")

    Returns:
        符合条件的文件路径元组

    Example:
        >>> files = listdir_with_allowed_type("./data", (".txt", ".pdf"))
        >>> print(files)
        ("./data/doc1.txt", "./data/doc2.pdf")
    """
    if not os.path.isdir(path):
        log_flow("FileHandler", f"[获取文件列表]: 路径{path}不是文件夹", level=40)
        return ()

    files = []
    for f in os.listdir(path):
        if f.endswith(allowed_types):
            files.append(os.path.join(path, f))

    return tuple(files)


def pdf_loader(filepath: str, passwd: str = None) -> List[Document]:
    """
    加载PDF文件

    Args:
        filepath: PDF文件路径
        passwd: PDF密码（可选）

    Returns:
        Document列表

    Example:
        >>> docs = pdf_loader("./data/doc.pdf")
        >>> print(len(docs))
        10
    """
    import logging
    # 临时抑制PDF解析器的调试输出
    pdf_logger = logging.getLogger("pdfminer")
    original_level = pdf_logger.level
    pdf_logger.setLevel(logging.WARNING)
    
    try:
        return PyPDFLoader(filepath, passwd).load()
    finally:
        pdf_logger.setLevel(original_level)


def text_loader(filepath: str) -> List[Document]:
    """
    加载文本文件

    Args:
        filepath: 文本文件路径

    Returns:
        Document列表

    Example:
        >>> docs = text_loader("./data/doc.txt")
        >>> print(len(docs))
        1
    """
    return TextLoader(filepath, encoding="utf-8").load()
