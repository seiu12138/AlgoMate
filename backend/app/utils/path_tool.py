#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author   : PR
# @Time     : 2026/3/18 15:08
# @File     : path_tool.py
# @Project  : AlgoMate
import os


def get_project_root() -> str:
    """
    获取项目根目录

    Returns:
        项目根目录的绝对路径

    Example:
        >>> root = get_project_root()
        >>> print(root)
        "/home/user/AlgoMate"
    """
    current_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file)
    project_root = os.path.dirname(current_dir)
    return project_root


def get_abs_path(relative_path: str) -> str:
    """
    将相对路径转换为绝对路径

    Args:
        relative_path: 相对路径

    Returns:
        绝对路径

    Example:
        >>> abs_path = get_abs_path("config/storage.yaml")
        >>> print(abs_path)
        "/home/user/AlgoMate/config/storage.yaml"
    """
    return os.path.join(get_project_root(), relative_path)
