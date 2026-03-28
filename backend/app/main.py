#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AlgoMate FastAPI 入口
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router


def create_app() -> FastAPI:
    """
    创建 FastAPI 应用实例
    
    Returns:
        FastAPI 应用实例
    """
    app = FastAPI(
        title="AlgoMate API",
        description="智能算法辅导系统 API - 基于 LangGraph + ReAct 架构",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
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
    
    return app


# 创建应用实例
app = create_app()


@app.get("/")
async def root():
    """根路径重定向到文档"""
    return {
        "message": "欢迎使用 AlgoMate API",
        "docs": "/docs",
        "api": "/api",
        "health": "/api/health"
    }


@app.get("/api")
async def api_root():
    """API 根路径"""
    return {
        "service": "AlgoMate API",
        "version": "0.1.0",
        "endpoints": {
            "health": "/api/health",
            "config": "/api/config",
            "rag_chat": "/api/rag/chat",
            "agent_solve": "/api/agent/solve",
            "session_clear": "/api/session/clear",
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
