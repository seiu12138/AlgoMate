#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
样式加载工具 - 用于加载外部 CSS 文件
"""

import streamlit as st
from pathlib import Path


def load_css(css_file_path: str) -> None:
    """
    加载 CSS 文件并注入到 Streamlit 页面
    
    Args:
        css_file_path: CSS 文件的相对路径或绝对路径
        
    Example:
        >>> load_css("style/algomate_theme.css")
    """
    # 获取项目根目录
    root_dir = Path(__file__).parent.parent
    
    # 构建完整路径
    css_path = root_dir / css_file_path
    
    if not css_path.exists():
        st.warning(f"⚠️ CSS 文件不存在: {css_path}")
        return
    
    try:
        with open(css_path, encoding="utf-8") as f:
            css_content = f.read()
        
        # 注入 CSS
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ 加载 CSS 文件失败: {e}")


def load_theme(theme_name: str = "algomate_theme") -> None:
    """
    加载主题样式
    
    Args:
        theme_name: 主题名称（默认: algomate_theme，对应 style/algomate_theme.css）
    """
    load_css(f"style/{theme_name}.css")
