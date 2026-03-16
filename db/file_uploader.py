#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author   : PR
# @Time     : 2026/3/16 15:53
# @File     : file_uploader.py
# @Project  : AlgoMate
import streamlit as st
from knowledge_base import KnowledgeBaseService

if "service" not in st.session_state:
    st.session_state["service"] = KnowledgeBaseService()


st.title("知识库更新服务")
uploader_file = st.file_uploader(
    label="文件上传",
    type=["txt"],
    accept_multiple_files=False
)

if uploader_file is not None:
    file_name = uploader_file.name
    file_type = uploader_file.type
    file_size = uploader_file.size / 1024

    st.subheader(f"文件名: {file_name}")
    st.write(f"格式: {file_type} | 大小: {file_size:.2f} KB")

    with st.spinner("文件载入知识库中..."):
        text = uploader_file.getvalue().decode("utf-8")
        result = st.session_state["service"].upload_by_str(text, file_name)
