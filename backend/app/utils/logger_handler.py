#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
日志处理模块
用于统一管理Agent流程中的日志记录
"""

import os
import logging
from datetime import datetime


def get_abs_path(relative_path: str) -> str:
    """获取相对于项目根目录的绝对路径"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_root, relative_path)


# 日志保存的根目录
LOG_ROOT = get_abs_path("logs")
os.makedirs(LOG_ROOT, exist_ok=True)

DEFAULT_LOG_FORMAT = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)


def get_logger(name: str = "agent", console_level: int = logging.INFO,
               file_level: int = logging.DEBUG, log_file=None) -> logging.Logger:
    """
    获取配置好的logger实例

    Args:
        name: logger名称
        console_level: 控制台日志级别
        file_level: 文件日志级别
        log_file: 日志文件路径，默认为logs/{name}_{date}.log

    Returns:
        配置好的Logger实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(console_handler)

    # 文件处理器
    if not log_file:
        log_file = os.path.join(LOG_ROOT, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(file_handler)

    return logger


# 预定义的logger实例
agent_logger = get_logger("agent")
node_logger = get_logger("agent.nodes")
react_logger = get_logger("agent.react")


# 便捷函数：记录特定流程的日志
def log_flow(flow_name: str, message: str, level: int = logging.INFO, logger_instance=None):
    """
    记录流程日志

    Args:
        flow_name: 流程名称（如Node、Agent等）
        message: 日志消息，格式为"[具体流程]: [发生了什么]"
        level: 日志级别
        logger_instance: 使用的logger实例，默认使用agent_logger
    """
    if logger_instance is None:
        logger_instance = agent_logger
    
    log_message = f"[{flow_name}]: {message}"
    logger_instance.log(level, log_message)


def log_node(node_name: str, message: str, level: int = logging.INFO):
    """记录节点流程日志"""
    log_flow(f"Node-{node_name}", message, level, node_logger)


def log_agent(message: str, level: int = logging.INFO):
    """记录Agent流程日志"""
    log_flow("Agent", message, level, react_logger)


def log_execution(message: str, level: int = logging.INFO):
    """记录执行流程日志"""
    log_flow("Execution", message, level, agent_logger)


def log_analysis(message: str, level: int = logging.INFO):
    """记录分析流程日志"""
    log_flow("Analysis", message, level, agent_logger)


def log_code(message: str, level: int = logging.INFO):
    """记录代码相关流程日志"""
    log_flow("Code", message, level, agent_logger)


def log_test(message: str, level: int = logging.INFO):
    """记录测试相关流程日志"""
    log_flow("Test", message, level, agent_logger)
