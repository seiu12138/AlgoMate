#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AlgoMate FastAPI 入口

AlgoMate - 智能算法辅导系统
基于 LangGraph + ReAct 架构的智能 Agent 系统

功能特性:
- RAG (检索增强生成): 知识问答
- Agent (智能体): 自动分析、编码、测试、修复
- Session (会话管理): 持久化对话历史

技术栈:
- FastAPI
- LangChain / LangGraph
- ChromaDB (向量数据库)
- SSE (服务器发送事件)
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html

from app.api.routes import router

# API 标签元数据
tags_metadata = [
    {
        "name": "Health",
        "description": "健康检查和系统状态",
    },
    {
        "name": "Sessions",
        "description": "会话管理 - 创建、查询、更新、删除会话",
    },
    {
        "name": "RAG",
        "description": "RAG (检索增强生成) - 知识库问答",
    },
    {
        "name": "Agent",
        "description": "智能 Agent - 自动分析题目、生成代码、执行测试、修复错误",
    },
    {
        "name": "System",
        "description": "系统配置和工具",
    },
]


def create_app() -> FastAPI:
    """
    创建 FastAPI 应用实例
    
    Returns:
        FastAPI 应用实例
    """
    app = FastAPI(
        title="AlgoMate API",
        description="""
# AlgoMate 智能算法辅导系统

基于 **LangGraph + ReAct** 架构的智能 Agent 系统

## 核心功能

### 1. RAG 模式 (知识问答)
- 向量检索增强生成
- 算法知识库查询
- 流式响应 (SSE)

### 2. Agent 模式 (智能解题)
- 自动分析算法题目
- 生成可执行代码 (Python/C++/Java)
- 自动生成测试用例
- 自动修复代码错误
- ReAct 循环迭代

### 3. Session 管理
- 会话持久化
- 消息历史记录
- 自动标题生成

## 认证
当前版本无需认证，后续将添加 API Key 支持

## 限流
- RAG: 无限制
- Agent: 建议 10 秒内最多 1 次请求
        """,
        version="0.1.0",
        docs_url=None,  # 禁用默认，使用自定义
        redoc_url=None,  # 禁用默认，使用自定义
        openapi_tags=tags_metadata,
        contact={
            "name": "AlgoMate Team",
            "url": "https://github.com/seiu12138/AlgoMate",
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT",
        },
    )
    
    # 配置 CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",  # Vite 开发服务器
            "http://localhost:4173",  # Vite Preview 服务器
            "http://localhost:3000",  # React 开发服务器
            "http://localhost:8080",  # 其他常见前端端口
            "http://127.0.0.1:5173",
            "http://127.0.0.1:4173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8080",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(router, prefix="/api")
    
    # 自定义 Swagger UI（使用国内 CDN）
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title="AlgoMate API - Swagger UI",
            swagger_js_url="https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.10.3/swagger-ui-bundle.min.js",
            swagger_css_url="https://cdn.bootcdn.net/ajax/libs/swagger-ui/5.10.3/swagger-ui.min.css",
            swagger_favicon_url="/favicon.svg",
        )
    
    # 自定义 ReDoc（使用国内 CDN）
    @app.get("/redoc", include_in_schema=False)
    async def custom_redoc_html():
        return get_redoc_html(
            openapi_url="/openapi.json",
            title="AlgoMate API - ReDoc",
            redoc_js_url="https://cdn.bootcdn.net/ajax/libs/redoc/2.1.3/redoc.standalone.min.js",
            redoc_favicon_url="/favicon.svg",
        )
    
    return app


# 创建应用实例
app = create_app()


@app.get("/", tags=["System"])
async def root():
    """
    根路径 - API 入口信息
    
    Returns:
        API 基本信息和文档链接
    """
    return {
        "message": "欢迎使用 AlgoMate API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "api": "/api",
        "health": "/api/health"
    }


@app.get("/api", tags=["System"])
async def api_root():
    """
    API 根路径 - 端点概览
    
    Returns:
        所有可用端点列表
    """
    return {
        "service": "AlgoMate API",
        "version": "0.1.0",
        "endpoints": {
            "health": "/api/health",
            "config": "/api/config",
            "sessions": {
                "list": "GET /api/sessions",
                "create": "POST /api/sessions",
                "get": "GET /api/sessions/{id}",
                "update": "PATCH /api/sessions/{id}",
                "delete": "DELETE /api/sessions/{id}",
            },
            "rag_chat": "POST /api/rag/chat",
            "agent_solve": "POST /api/agent/solve",
        }
    }


# 如果直接运行此文件
if __name__ == "__main__":
    import uvicorn
    
    # 从环境变量获取配置，或使用默认值
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print(f"🚀 启动 AlgoMate API 服务器...")
    print(f"📍 地址: http://{host}:{port}")
    print(f"📚 文档: http://{host}:{port}/docs")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
