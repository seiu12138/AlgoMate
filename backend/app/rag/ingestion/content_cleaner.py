#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Content cleaner for web search results.
Extracts valuable content and removes noise.
"""
import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse


@dataclass
class CleanedContent:
    """清洗后的内容"""
    title: str = ""
    url: str = ""
    algorithm_name: str = ""
    core_concept: str = ""
    cleaned_content: str = ""  # 清洗后的正文
    code_blocks: List[Dict[str, str]] = field(default_factory=list)
    complexity: Dict[str, str] = field(default_factory=dict)
    solution_steps: List[str] = field(default_factory=list)
    confidence: float = 0.0  # 清洗置信度


class ContentCleaner:
    """
    网页内容清洗器
    
    目标：
    1. 提取正文内容，去除噪声
    2. 识别并提取代码块
    3. 提取结构化信息（算法名、复杂度等）
    """
    
    # 常见噪声模式
    NOISE_PATTERNS = [
        r'相关文章\s*[：:]?\s*\n.*',
        r'推荐阅读\s*[：:]?\s*\n.*',
        r'广告.*?\n',
        r' Sponsored \s*Content.*',
        r'\[.*?(订阅|关注|点赞|分享).*?\]',
        r'© \d{4}.*?(版权所有|All Rights Reserved)',
        r'上一篇：.*?下一篇：.*?',
        r'热门标签[：:].*',
    ]
    
    # 代码块标记
    CODE_MARKERS = [
        (r'```(\w+)?\s*\n(.*?)```', 'markdown'),
        (r'<code[^>]*>(.*?)</code>', 'html'),
        (r'<pre[^>]*>(.*?)</pre>', 'html'),
    ]
    
    def __init__(self, min_content_length: int = 200, max_content_length: int = 10000):
        """
        初始化清洗器
        
        Args:
            min_content_length: 最小内容长度
            max_content_length: 最大内容长度
        """
        self.min_content_length = min_content_length
        self.max_content_length = max_content_length
        self.noise_regex = [re.compile(p, re.DOTALL | re.IGNORECASE) for p in self.NOISE_PATTERNS]
    
    def clean(self, html_content: str, url: str, title: str = "") -> Optional[CleanedContent]:
        """
        清洗HTML内容
        
        Args:
            html_content: 原始HTML
            url: 来源URL
            title: 页面标题
            
        Returns:
            清洗后的内容，失败返回None
        """
        try:
            # 1. 提取正文
            text = self._extract_text(html_content)
            if not text or len(text) < self.min_content_length:
                return None
            
            # 2. 去除噪声
            text = self._remove_noise(text)
            
            # 3. 提取代码块
            code_blocks, text_without_code = self._extract_code_blocks(text)
            
            # 4. 提取结构化信息
            structured = self._extract_structured_info(text)
            
            # 5. 截断过长内容
            if len(text) > self.max_content_length:
                text = text[:self.max_content_length] + "\n...(内容已截断)"
            
            # 6. 计算置信度
            confidence = self._calculate_confidence(
                text, code_blocks, structured, url
            )
            
            return CleanedContent(
                title=title or structured.get("title", ""),
                url=url,
                algorithm_name=structured.get("algorithm_name", ""),
                core_concept=structured.get("core_concept", ""),
                cleaned_content=text_without_code or text,
                code_blocks=code_blocks,
                complexity=structured.get("complexity", {}),
                solution_steps=structured.get("solution_steps", []),
                confidence=confidence
            )
            
        except Exception as e:
            print(f"[ContentCleaner] Failed to clean content from {url}: {e}")
            return None
    
    def _extract_text(self, html: str) -> str:
        """从HTML提取正文"""
        try:
            # 优先使用trafilatura
            import trafilatura
            text = trafilatura.extract(
                html,
                include_comments=False,
                include_tables=True,
                no_fallback=False,
                include_images=False,
                include_links=False
            )
            if text:
                return text
        except ImportError:
            pass
        
        # 降级：使用简单HTML解析
        return self._simple_html_to_text(html)
    
    def _simple_html_to_text(self, html: str) -> str:
        """简单HTML到文本转换"""
        from html.parser import HTMLParser
        
        class TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text = []
                self.skip_tags = {'script', 'style', 'nav', 'footer', 'header', 'aside'}
                self.current_tag = None
                self.skip_depth = 0
            
            def handle_starttag(self, tag, attrs):
                if tag in self.skip_tags:
                    self.skip_depth += 1
                self.current_tag = tag
            
            def handle_endtag(self, tag):
                if tag in self.skip_tags:
                    self.skip_depth -= 1
                if tag in ['p', 'div', 'br', 'h1', 'h2', 'h3', 'h4', 'li']:
                    self.text.append('\n')
            
            def handle_data(self, data):
                if self.skip_depth == 0:
                    self.text.append(data)
        
        extractor = TextExtractor()
        try:
            extractor.feed(html)
            text = ''.join(extractor.text)
            # 清理多余空白
            text = re.sub(r'\n\s*\n+', '\n\n', text)
            text = re.sub(r'[ \t]+', ' ', text)
            return text.strip()
        except:
            return ""
    
    def _remove_noise(self, text: str) -> str:
        """去除噪声内容"""
        for pattern in self.noise_regex:
            text = pattern.sub('', text)
        
        # 去除多余空行
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def _extract_code_blocks(self, text: str) -> tuple:
        """
        提取代码块
        
        Returns:
            (code_blocks列表, 去除代码后的文本)
        """
        code_blocks = []
        text_without_code = text
        
        # Markdown代码块 ```lang\ncode```
        md_pattern = r'```(\w+)?\s*\n(.*?)```'
        for match in re.finditer(md_pattern, text, re.DOTALL):
            lang = match.group(1) or "text"
            code = match.group(2).strip()
            if len(code) > 20:  # 过滤太短的代码
                code_blocks.append({
                    "language": lang,
                    "code": code
                })
        
        # 移除代码块后的文本
        text_without_code = re.sub(md_pattern, '[代码块]', text, flags=re.DOTALL)
        
        # HTML <code>标签
        html_code_pattern = r'<code[^>]*>(.*?)</code>'
        for match in re.finditer(html_code_pattern, text_without_code, re.DOTALL):
            code = match.group(1).strip()
            if len(code) > 10 and len(code) < 200:
                code_blocks.append({
                    "language": "text",
                    "code": code
                })
        
        text_without_code = re.sub(html_code_pattern, '', text_without_code)
        
        # 缩进代码块 (4空格或Tab)
        indent_pattern = r'(?:^|\n)(?:    |\t)(.+?)(?=\n[^\t ])'
        for match in re.finditer(indent_pattern, text_without_code, re.DOTALL):
            code = match.group(1).strip()
            if len(code) > 30:
                code_blocks.append({
                    "language": "text",
                    "code": code
                })
        
        return code_blocks, text_without_code
    
    def _extract_structured_info(self, text: str) -> Dict[str, Any]:
        """提取结构化信息"""
        result = {
            "title": "",
            "algorithm_name": "",
            "core_concept": "",
            "complexity": {},
            "solution_steps": []
        }
        
        # 提取算法名称 (常见模式)
        algo_patterns = [
            r'([\u4e00-\u9fa5\w\s]+)(?:算法|Algorithm)',
            r'什么是([\u4e00-\u9fa5\w\s]+?)？',
            r'([\u4e00-\u9fa5\w\s]+?)(?:详解|入门|教程)',
        ]
        for pattern in algo_patterns:
            match = re.search(pattern, text[:500], re.IGNORECASE)
            if match:
                result["algorithm_name"] = match.group(1).strip()
                break
        
        # 提取复杂度信息
        time_pattern = r'时间复杂度[：:]\s*([OΘΩo][\(\)nw\s\d\+\-\*\/log]+)'
        space_pattern = r'空间复杂度[：:]\s*([OΘΩo][\(\)nw\s\d\+\-\*\/log]+)'
        
        time_match = re.search(time_pattern, text, re.IGNORECASE)
        space_match = re.search(space_pattern, text, re.IGNORECASE)
        
        if time_match:
            result["complexity"]["time"] = time_match.group(1)
        if space_match:
            result["complexity"]["space"] = space_match.group(1)
        
        # 提取解题步骤 (数字或项目符号开头)
        step_pattern = r'(?:^|\n)(?:\d+[.．、]|[-•*])[ \t]*(.+?)(?=\n(?:\d+[.．、]|[-•*])|$)'
        steps = re.findall(step_pattern, text, re.MULTILINE)
        result["solution_steps"] = [s.strip() for s in steps[:10] if len(s.strip()) > 5]
        
        # 提取核心概念 (前200字)
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if lines:
            result["core_concept"] = lines[0][:200]
        
        return result
    
    def _calculate_confidence(
        self,
        text: str,
        code_blocks: List[Dict],
        structured: Dict,
        url: str
    ) -> float:
        """
        计算清洗置信度
        
        评分因素：
        - 内容长度
        - 代码块数量
        - 结构化信息完整度
        - 来源可靠性
        """
        score = 0.0
        
        # 内容长度 (0-0.3)
        length_score = min(1.0, len(text) / 2000) * 0.3
        score += length_score
        
        # 代码块 (0-0.3)
        code_score = min(1.0, len(code_blocks) / 3) * 0.3
        score += code_score
        
        # 结构化信息 (0-0.3)
        struct_score = 0.0
        if structured.get("algorithm_name"):
            struct_score += 0.1
        if structured.get("complexity"):
            struct_score += 0.1
        if structured.get("solution_steps"):
            struct_score += 0.1
        score += struct_score
        
        # 来源可靠性 (0-0.1)
        reliable_domains = [
            'leetcode', 'github', 'geeksforgeeks', 
            'wikipedia', 'cnblogs', 'csdn', 'juejin', 'zhihu'
        ]
        domain = urlparse(url).netloc.lower()
        if any(d in domain for d in reliable_domains):
            score += 0.1
        
        return min(1.0, score)


# 便捷函数
def clean_web_content(
    html_content: str,
    url: str,
    title: str = ""
) -> Optional[CleanedContent]:
    """
    便捷的网页内容清洗函数
    
    Args:
        html_content: HTML内容
        url: 来源URL
        title: 页面标题
        
    Returns:
        清洗后的内容
    """
    cleaner = ContentCleaner()
    return cleaner.clean(html_content, url, title)
