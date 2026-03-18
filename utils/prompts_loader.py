#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Prompts Loader Module
用于加载各种prompt模板文件
"""

import os
import yaml
import logging

logger = logging.getLogger(__name__)

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 加载prompts配置
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config", "prompts.yaml")

def _load_config():
    """加载yaml配置文件"""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"[Prompts加载]: 加载配置文件出错: {str(e)}")
        raise e

def _get_abs_path(relative_path):
    """将相对路径转换为绝对路径"""
    return os.path.join(PROJECT_ROOT, relative_path)

# 缓存配置
_prompts_conf = None

def get_prompts_conf():
    """获取prompts配置（带缓存）"""
    global _prompts_conf
    if _prompts_conf is None:
        _prompts_conf = _load_config()
    return _prompts_conf


def load_analysis_prompt():
    """
    加载题目分析prompt

    Returns:
        ANALYSIS_PROMPT的内容
    """
    prompts_conf = get_prompts_conf()
    try:
        prompt_path = _get_abs_path(prompts_conf["ANALYSIS_PROMPT"])
    except KeyError as e:
        logger.error(f"[Prompts加载]: yaml配置项中找不到ANALYSIS_PROMPT配置项")
        raise e

    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"[Prompts加载]: 加载ANALYSIS_PROMPT出错: {str(e)}")
        raise e


def load_test_case_generation_prompt():
    """
    加载测试用例生成prompt

    Returns:
        TEST_CASE_GENERATION_PROMPT的内容
    """
    prompts_conf = get_prompts_conf()
    try:
        prompt_path = _get_abs_path(prompts_conf["TEST_CASE_GENERATION_PROMPT"])
    except KeyError as e:
        logger.error(f"[Prompts加载]: yaml配置项中找不到TEST_CASE_GENERATION_PROMPT配置项")
        raise e

    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"[Prompts加载]: 加载TEST_CASE_GENERATION_PROMPT出错: {str(e)}")
        raise e


def load_code_generation_prompt():
    """
    加载代码生成prompt

    Returns:
        CODE_GENERATION_PROMPT的内容
    """
    prompts_conf = get_prompts_conf()
    try:
        prompt_path = _get_abs_path(prompts_conf["CODE_GENERATION_PROMPT"])
    except KeyError as e:
        logger.error(f"[Prompts加载]: yaml配置项中找不到CODE_GENERATION_PROMPT配置项")
        raise e

    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"[Prompts加载]: 加载CODE_GENERATION_PROMPT出错: {str(e)}")
        raise e


def load_test_case_validation_prompt():
    """
    加载测试用例验证prompt

    Returns:
        TEST_CASE_VALIDATION_PROMPT的内容
    """
    prompts_conf = get_prompts_conf()
    try:
        prompt_path = _get_abs_path(prompts_conf["TEST_CASE_VALIDATION_PROMPT"])
    except KeyError as e:
        logger.error(f"[Prompts加载]: yaml配置项中找不到TEST_CASE_VALIDATION_PROMPT配置项")
        raise e

    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"[Prompts加载]: 加载TEST_CASE_VALIDATION_PROMPT出错: {str(e)}")
        raise e


def load_code_fix_prompt():
    """
    加载代码修复prompt

    Returns:
        CODE_FIX_PROMPT的内容
    """
    prompts_conf = get_prompts_conf()
    try:
        prompt_path = _get_abs_path(prompts_conf["CODE_FIX_PROMPT"])
    except KeyError as e:
        logger.error(f"[Prompts加载]: yaml配置项中找不到CODE_FIX_PROMPT配置项")
        raise e

    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"[Prompts加载]: 加载CODE_FIX_PROMPT出错: {str(e)}")
        raise e


def load_final_answer_prompt():
    """
    加载最终答案生成prompt

    Returns:
        FINAL_ANSWER_PROMPT的内容
    """
    prompts_conf = get_prompts_conf()
    try:
        prompt_path = _get_abs_path(prompts_conf["FINAL_ANSWER_PROMPT"])
    except KeyError as e:
        logger.error(f"[Prompts加载]: yaml配置项中找不到FINAL_ANSWER_PROMPT配置项")
        raise e

    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"[Prompts加载]: 加载FINAL_ANSWER_PROMPT出错: {str(e)}")
        raise e


# 便捷函数：加载所有prompts
def load_all_prompts():
    """
    加载所有prompts

    Returns:
        包含所有prompt的字典
    """
    return {
        "ANALYSIS_PROMPT": load_analysis_prompt(),
        "TEST_CASE_GENERATION_PROMPT": load_test_case_generation_prompt(),
        "CODE_GENERATION_PROMPT": load_code_generation_prompt(),
        "TEST_CASE_VALIDATION_PROMPT": load_test_case_validation_prompt(),
        "CODE_FIX_PROMPT": load_code_fix_prompt(),
        "FINAL_ANSWER_PROMPT": load_final_answer_prompt(),
    }


if __name__ == "__main__":
    # 测试加载所有prompts
    print("测试加载所有prompts...")
    prompts = load_all_prompts()
    for name, content in prompts.items():
        print(f"\n{name}: {len(content)} 字符")
    print("\n所有prompts加载成功！")
