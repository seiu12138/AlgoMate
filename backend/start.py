#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AlgoMate Backend 启动脚本
包含环境检查和一键启动功能
"""
import os
import sys


def check_environment():
    """检查运行环境"""
    print("🔍 环境检查...")
    
    # 检查 Python 版本
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"✗ 需要 Python 3.8+, 当前 {version.major}.{version.minor}")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    
    # 检查关键依赖
    try:
        import fastapi
        print(f"✓ FastAPI {fastapi.__version__}")
    except ImportError:
        print("✗ FastAPI 未安装，请运行: pip install -r requirements.txt")
        return False
    
    try:
        import uvicorn
        print("✓ Uvicorn 已安装")
    except ImportError:
        print("✗ Uvicorn 未安装")
        return False
    
    # 检查 API Key
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if api_key:
        print(f"✓ DASHSCOPE_API_KEY 已设置 ({api_key[:8]}...)")
    else:
        print("⚠️  DASHSCOPE_API_KEY 未设置，AI 功能将不可用")
        print("    请设置: $env:DASHSCOPE_API_KEY='your-key'")
    
    return True


def main():
    """主函数"""
    # 检查环境
    if not check_environment():
        sys.exit(1)
    
    # 启动参数
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print("\n" + "=" * 60)
    print("🚀 AlgoMate Backend 启动中...")
    print("=" * 60)
    print(f"📍 地址: http://{host}:{port}")
    print(f"📚 文档: http://{host}:{port}/docs")
    print(f"🔧 健康: http://{host}:{port}/api/health")
    print("=" * 60 + "\n")
    
    # 启动服务
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()
