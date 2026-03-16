#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author   : PR
# @Time     : 2026/3/16 16:02
# @File     : config_data.py
# @Project  : AlgoMate

# md5文件存储路径
md5_path = "./data/md5.text"

# chroma数据库存储路径
collection_name = "algomate"
persist_directory = "./data/chromd_db"

# splitter相关配置
chunk_size = 1000
chunk_overlap = 100
separators = ["\n\n", "\n", ".", "!", "?", "。", "？", "！", " ", ""]
max_split_char_number = 1000

# 相似度检索相关配置
max_search_key = 2

# 模型相关配置
embedding_model_name = "text-embedding-v4"
chat_model_name = "qwen3-max"

# 记忆历史相关
history_path = "./data/chat_history"