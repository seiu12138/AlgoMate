#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Web search tool for RAG enhancement.
Supports DuckDuckGo (free) and Bing API (production).
"""
import asyncio
import hashlib
import json
import time
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse

import aiohttp
from langchain_core.documents import Document


@dataclass
class WebSearchResult:
    """网页搜索结果"""
    title: str
    url: str
    snippet: str
    content: Optional[str] = None  # 抓取后的正文
    source: str = "unknown"  # 搜索提供商
    timestamp: float = 0
    
    def to_document(self) -> Document:
        """转换为LangChain Document"""
        return Document(
            page_content=self.content or self.snippet,
            metadata={
                "title": self.title,
                "url": self.url,
                "snippet": self.snippet,
                "source": self.source,
                "timestamp": self.timestamp
            }
        )


class WebSearchTool:
    """
    网页搜索工具
    
    支持多种搜索提供商:
    - duckduckgo: 免费，无需API Key
    - bing: 需要Azure订阅，质量更高
    """
    
    def __init__(
        self,
        provider: str = "duckduckgo",
        api_key: Optional[str] = None,
        max_results: int = 5,
        cache_ttl: int = 3600,
        timeout: int = 10
    ):
        self.provider = provider.lower()
        self.api_key = api_key
        self.max_results = max_results
        self.cache_ttl = cache_ttl
        self.timeout = timeout
        
        # 简单内存缓存
        self._cache: Dict[str, Dict] = {}
        
        # 验证提供商
        if self.provider not in ["duckduckgo", "bing"]:
            raise ValueError(f"Unsupported provider: {provider}")
        
        if self.provider == "bing" and not api_key:
            raise ValueError("Bing API requires api_key")
    
    def _get_cache_key(self, query: str) -> str:
        """生成缓存键"""
        return hashlib.md5(f"{self.provider}:{query}".encode()).hexdigest()
    
    def _get_from_cache(self, query: str) -> Optional[List[WebSearchResult]]:
        """从缓存获取结果"""
        key = self._get_cache_key(query)
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry["timestamp"] < self.cache_ttl:
                return entry["results"]
            else:
                del self._cache[key]
        return None
    
    def _save_to_cache(self, query: str, results: List[WebSearchResult]):
        """保存结果到缓存"""
        key = self._get_cache_key(query)
        self._cache[key] = {
            "timestamp": time.time(),
            "results": results
        }
    
    async def search(self, query: str) -> List[WebSearchResult]:
        """
        执行网页搜索
        
        Args:
            query: 搜索查询
            
        Returns:
            搜索结果列表
        """
        # 检查缓存
        cached = self._get_from_cache(query)
        if cached:
            return cached
        
        # 根据提供商执行搜索
        if self.provider == "duckduckgo":
            results = await self._search_duckduckgo(query)
        elif self.provider == "bing":
            results = await self._search_bing(query)
        else:
            results = []
        
        # 保存缓存
        self._save_to_cache(query, results)
        
        return results
    
    async def _search_duckduckgo(self, query: str) -> List[WebSearchResult]:
        """使用DuckDuckGo搜索 (使用新版 ddgs 库)"""
        try:
            # 使用新版 ddgs 库 (duckduckgo-search 的新名称)
            from ddgs import DDGS
            
            results = []
            with DDGS() as ddgs:
                # 新版 API 参数略有不同
                search_results = ddgs.text(
                    query,
                    max_results=self.max_results,
                    region="wt-wt"  # 全球结果，无区域限制
                )
                
                for r in search_results:
                    results.append(WebSearchResult(
                        title=r.get("title", ""),
                        url=r.get("href", ""),
                        snippet=r.get("body", ""),
                        source="duckduckgo",
                        timestamp=time.time()
                    ))
            
            return results
            
        except Exception as e:
            print(f"[WebSearch] DuckDuckGo search failed: {e}")
            # 降级：返回空结果，但不影响整体流程
            return []
    
    async def _search_bing(self, query: str) -> List[WebSearchResult]:
        """使用Bing API搜索"""
        try:
            url = "https://api.bing.microsoft.com/v7.0/search"
            headers = {"Ocp-Apim-Subscription-Key": self.api_key}
            params = {
                "q": query,
                "count": self.max_results,
                "mkt": "zh-CN",
                "responseFilter": "Webpages"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, 
                    headers=headers, 
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status != 200:
                        print(f"[WebSearch] Bing API error: {response.status}")
                        return []
                    
                    data = await response.json()
                    web_pages = data.get("webPages", {}).get("value", [])
                    
                    results = []
                    for page in web_pages:
                        results.append(WebSearchResult(
                            title=page.get("name", ""),
                            url=page.get("url", ""),
                            snippet=page.get("snippet", ""),
                            source="bing",
                            timestamp=time.time()
                        ))
                    
                    return results
                    
        except Exception as e:
            print(f"[WebSearch] Bing search failed: {e}")
            return []
    
    async def fetch_content(
        self, 
        url: str, 
        max_length: int = 5000
    ) -> Optional[str]:
        """
        抓取网页正文内容
        
        Args:
            url: 网页URL
            max_length: 最大内容长度
            
        Returns:
            清洗后的正文内容
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0"
                    }
                ) as response:
                    if response.status != 200:
                        return None
                    
                    html = await response.text()
                    
                    # 使用trafilatura提取正文
                    try:
                        import trafilatura
                        content = trafilatura.extract(
                            html,
                            include_comments=False,
                            include_tables=True,
                            no_fallback=False
                        )
                    except ImportError:
                        # 降级：简单HTML清理
                        content = self._simple_html_clean(html)
                    
                    if content and len(content) > max_length:
                        content = content[:max_length] + "..."
                    
                    return content
                    
        except Exception as e:
            print(f"[WebSearch] Failed to fetch {url}: {e}")
            return None
    
    def _simple_html_clean(self, html: str) -> str:
        """简单HTML清理 (降级方案)"""
        from html.parser import HTMLParser
        
        class TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text = []
                self.skip_tags = {"script", "style", "nav", "footer", "header"}
                self.current_tag = None
            
            def handle_starttag(self, tag, attrs):
                self.current_tag = tag
            
            def handle_endtag(self, tag):
                self.current_tag = None
            
            def handle_data(self, data):
                if self.current_tag not in self.skip_tags:
                    self.text.append(data.strip())
        
        extractor = TextExtractor()
        try:
            extractor.feed(html)
            return " ".join(extractor.text)
        except:
            return ""
    
    async def search_and_fetch(
        self, 
        query: str, 
        fetch_content: bool = True
    ) -> List[WebSearchResult]:
        """
        搜索并抓取内容
        
        Args:
            query: 搜索查询
            fetch_content: 是否抓取网页正文
            
        Returns:
            带正文的搜索结果
        """
        # 执行搜索
        results = await self.search(query)
        
        if not fetch_content:
            return results
        
        # 并发抓取内容
        async def fetch_with_limit(result: WebSearchResult) -> WebSearchResult:
            content = await self.fetch_content(result.url)
            if content:
                result.content = content
            return result
        
        # 限制并发数
        semaphore = asyncio.Semaphore(3)
        
        async def bounded_fetch(result):
            async with semaphore:
                return await fetch_with_limit(result)
        
        tasks = [bounded_fetch(r) for r in results]
        fetched_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 过滤错误结果
        valid_results = []
        for r in fetched_results:
            if isinstance(r, Exception):
                continue
            valid_results.append(r)
        
        return valid_results


# 便捷函数
async def web_search(
    query: str,
    provider: str = "duckduckgo",
    api_key: Optional[str] = None,
    max_results: int = 5,
    fetch_content: bool = True
) -> List[WebSearchResult]:
    """
    便捷的网页搜索函数
    
    Args:
        query: 搜索查询
        provider: 搜索提供商 (duckduckgo/bing)
        api_key: API密钥 (Bing必需)
        max_results: 最大结果数
        fetch_content: 是否抓取正文
        
    Returns:
        搜索结果列表
    """
    tool = WebSearchTool(
        provider=provider,
        api_key=api_key,
        max_results=max_results
    )
    return await tool.search_and_fetch(query, fetch_content)


if __name__ == "__main__":
    # 测试
    async def test():
        results = await web_search(
            "python 动态规划教程",
            provider="duckduckgo",
            max_results=3
        )
        for r in results:
            print(f"\nTitle: {r.title}")
            print(f"URL: {r.url}")
            print(f"Snippet: {r.snippet[:100]}...")
            if r.content:
                print(f"Content: {r.content[:200]}...")
    
    asyncio.run(test())
