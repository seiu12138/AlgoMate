#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置处理模块
用于统一管理项目配置文件的加载
"""

import os
import yaml


def get_abs_path(relative_path: str) -> str:
    """获取相对于项目根目录的绝对路径"""
    # 获取当前文件所在目录 (backend/app/utils/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 向上两级到 backend/app/
    app_dir = os.path.dirname(current_dir)
    # 拼接目标路径
    return os.path.join(app_dir, relative_path)


def load_storage_config(config_path: str = None, encoding: str = 'utf-8') -> dict:
    """
    加载存储路径配置
    
    Args:
        config_path: 配置文件路径，默认为 config/storage.yaml
        encoding: 文件编码
        
    Returns:
        存储配置字典
    """
    if config_path is None:
        config_path = get_abs_path("config/storage.yaml")
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_chroma_config(config_path: str = None, encoding: str = 'utf-8') -> dict:
    """
    加载Chroma向量数据库配置
    
    Args:
        config_path: 配置文件路径，默认为 config/chroma.yaml
        encoding: 文件编码
        
    Returns:
        Chroma配置字典
    """
    if config_path is None:
        config_path = get_abs_path("config/chroma.yaml")
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_splitter_config(config_path: str = None, encoding: str = 'utf-8') -> dict:
    """
    加载文本分割器配置
    
    Args:
        config_path: 配置文件路径，默认为 config/splitter.yaml
        encoding: 文件编码
        
    Returns:
        分割器配置字典
    """
    if config_path is None:
        config_path = get_abs_path("config/splitter.yaml")
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_search_config(config_path: str = None, encoding: str = 'utf-8') -> dict:
    """
    加载相似度检索配置
    
    Args:
        config_path: 配置文件路径，默认为 config/search.yaml
        encoding: 文件编码
        
    Returns:
        检索配置字典
    """
    if config_path is None:
        config_path = get_abs_path("config/search.yaml")
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_model_config(config_path: str = None, encoding: str = 'utf-8') -> dict:
    """
    加载AI模型配置
    
    Args:
        config_path: 配置文件路径，默认为 config/model.yaml
        encoding: 文件编码
        
    Returns:
        模型配置字典
    """
    if config_path is None:
        config_path = get_abs_path("config/model.yaml")
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_session_config(config_path: str = None, encoding: str = 'utf-8') -> dict:
    """
    加载会话配置
    
    Args:
        config_path: 配置文件路径，默认为 config/session.yaml
        encoding: 文件编码
        
    Returns:
        会话配置字典
    """
    if config_path is None:
        config_path = get_abs_path("config/session.yaml")
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_prompts_config(config_path: str = None, encoding: str = 'utf-8') -> dict:
    """
    加载Prompts配置
    
    Args:
        config_path: 配置文件路径，默认为 config/prompts.yaml
        encoding: 文件编码
        
    Returns:
        Prompts配置字典
    """
    if config_path is None:
        config_path = get_abs_path("config/prompts.yaml")
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_agent_config(config_path: str = None, encoding: str = 'utf-8') -> dict:
    """
    加载Agent配置
    
    Args:
        config_path: 配置文件路径，默认为 config/agent.yaml
        encoding: 文件编码
        
    Returns:
        Agent配置字典
    """
    if config_path is None:
        config_path = get_abs_path("config/agent.yaml")
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


# 预加载的配置实例（缓存）
_storage_conf = None
_chroma_conf = None
_splitter_conf = None
_search_conf = None
_model_conf = None
_session_conf = None
_prompts_conf = None
_agent_conf = None


def get_storage_config() -> dict:
    """获取存储配置（带缓存）"""
    global _storage_conf
    if _storage_conf is None:
        _storage_conf = load_storage_config()
    return _storage_conf


def get_chroma_config() -> dict:
    """获取Chroma配置（带缓存）"""
    global _chroma_conf
    if _chroma_conf is None:
        _chroma_conf = load_chroma_config()
    return _chroma_conf


def get_splitter_config() -> dict:
    """获取分割器配置（带缓存）"""
    global _splitter_conf
    if _splitter_conf is None:
        _splitter_conf = load_splitter_config()
    return _splitter_conf


def get_search_config() -> dict:
    """获取检索配置（带缓存）"""
    global _search_conf
    if _search_conf is None:
        _search_conf = load_search_config()
    return _search_conf


def get_model_config() -> dict:
    """获取模型配置（带缓存）"""
    global _model_conf
    if _model_conf is None:
        _model_conf = load_model_config()
    return _model_conf


def get_session_config() -> dict:
    """获取会话配置（带缓存）"""
    global _session_conf
    if _session_conf is None:
        _session_conf = load_session_config()
    return _session_conf


def get_prompts_config() -> dict:
    """获取Prompts配置（带缓存）"""
    global _prompts_conf
    if _prompts_conf is None:
        _prompts_conf = load_prompts_config()
    return _prompts_conf


def get_agent_config() -> dict:
    """获取Agent配置（带缓存）"""
    global _agent_conf
    if _agent_conf is None:
        _agent_conf = load_agent_config()
    return _agent_conf


# 便捷导出
storage_conf = get_storage_config()
chroma_conf = get_chroma_config()
splitter_conf = get_splitter_config()
search_conf = get_search_config()
model_conf = get_model_config()
session_conf = get_session_config()
prompts_conf = get_prompts_config()
agent_conf = get_agent_config()
