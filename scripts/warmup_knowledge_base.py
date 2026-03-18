#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author   : PR
# @Time     : 2026/3/18
# @File     : warmup_knowledge_base.py
# @Project  : AlgoMate
"""
知识库预热脚本

用于将 data/knowledge_base 目录中的文件加载到 Chroma 向量数据库中。
支持增量加载，已加载过的文件（通过MD5校验）会自动跳过。

预热时间参考（DashScope text-embedding-v4）：
- leetcode.pdf (~27MB): 约 3-5 分钟
- OI-wiki.pdf (~49MB): 约 5-8 分钟
- 总计: 约 8-13 分钟

Usage:
    python scripts/warmup_knowledge_base.py [--test-query "你的测试查询"]
"""
import argparse
import os
import sys
import time

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from langchain_community.embeddings import DashScopeEmbeddings

from rag.vector_stores import VectorStoreService
from utils.config_handler import model_conf
from utils.logger_handler import log_flow


def warmup_knowledge_base(test_query: str = None):
    """
    执行知识库预热

    将配置目录中的文档加载到Chroma向量数据库。

    Args:
        test_query: 预热完成后执行的测试查询，为None则不测试
    """
    log_flow("Warmup", "[知识库预热]: 开始加载知识库文件...")
    start_time = time.time()

    try:
        # 初始化嵌入模型
        embedding = DashScopeEmbeddings(model=model_conf['embedding_model_name'])

        # 初始化向量存储服务
        vector_service = VectorStoreService(embedding=embedding)

        # 加载文档
        total_chunks = vector_service.load_document()

        elapsed = time.time() - start_time
        log_flow("Warmup", f"[知识库预热]: 知识库预热完成，新增 {total_chunks} 个文档片段，耗时 {elapsed:.1f} 秒")

        # 执行检索测试
        if test_query:
            print("\n")
            vector_service.test_retrieval(test_query)

    except Exception as e:
        log_flow("Warmup", f"[知识库预热]: 预热失败 - {str(e)}", level=40)
        raise


def main():
    parser = argparse.ArgumentParser(description="知识库预热脚本")
    parser.add_argument(
        "--test-query",
        type=str,
        default="动态规划",
        help="预热完成后执行的测试查询（默认: 动态规划）"
    )
    parser.add_argument(
        "--no-test",
        action="store_true",
        help="跳过检索测试"
    )

    args = parser.parse_args()

    query = None if args.no_test else args.test_query
    warmup_knowledge_base(test_query=query)


if __name__ == "__main__":
    main()
