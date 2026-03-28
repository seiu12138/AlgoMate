#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AlgoMate Mock Backend - 用于前端测试
"""
import asyncio
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel, Field
from typing import List

app = FastAPI(title="AlgoMate Mock API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:4173", "http://127.0.0.1:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求模型
class RAGChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class AgentSolveRequest(BaseModel):
    problem: str
    language: str = "python"
    max_iterations: int = 5
    session_id: str = "default"

class SessionClearRequest(BaseModel):
    session_id: str = "default"

# 健康检查
@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "AlgoMate Mock API"}

# 配置
@app.get("/api/config")
async def config():
    return {
        "languages": ["python", "cpp", "java"],
        "max_iterations_range": [1, 10]
    }

# RAG 流式响应
async def rag_stream(message: str):
    """模拟 RAG 流式响应"""
    response = "这是对问题的模拟回答。动态规划是一种通过把原问题分解为相对简单的子问题的方式来求解复杂问题的方法。"
    
    for word in response:
        yield {
            "event": "message",
            "data": json.dumps({"type": "token", "content": word}, ensure_ascii=False)
        }
        await asyncio.sleep(0.02)
    
    yield {
        "event": "message",
        "data": json.dumps({"type": "done"}, ensure_ascii=False)
    }

@app.post("/api/rag/chat")
async def rag_chat(request: RAGChatRequest):
    return EventSourceResponse(rag_stream(request.message))

# Agent 流式响应
async def agent_stream(problem: str, language: str):
    """模拟 Agent 流式响应"""
    nodes = [
        ("analyze", "分析题目...", 10),
        ("generate_test_cases", "生成测试用例...", 25),
        ("validate_test_cases", "验证测试用例...", 40),
        ("generate_code", "生成代码...", 60),
        ("execute_code", "执行代码...", 75),
        ("analyze_result", "分析结果...", 90),
        ("finish", "完成...", 100),
    ]
    
    for node, status, progress in nodes:
        yield {
            "event": "message",
            "data": json.dumps({
                "type": "node_start",
                "node": node,
                "status": status
            }, ensure_ascii=False)
        }
        
        yield {
            "event": "message",
            "data": json.dumps({
                "type": "progress",
                "value": progress
            }, ensure_ascii=False)
        }
        
        yield {
            "event": "message",
            "data": json.dumps({
                "type": "node_complete",
                "node": node,
                "output": {}
            }, ensure_ascii=False)
        }
        
        await asyncio.sleep(0.5)
    
    # 最终结果
    result = {
        "final_answer": "已为您生成代码解决这个问题。",
        "is_solved": True,
        "generated_code": "def solution(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        complement = target - num\n        if complement in seen:\n            return [seen[complement], i]\n        seen[num] = i\n    return []",
        "language": language,
        "iteration_count": 1,
        "execution_history": [
            {
                "iteration": 1,
                "code": "def solution(nums, target):...",
                "result": {"success": True, "stdout": "用例 1: [成功]"}
            }
        ]
    }
    
    yield {
        "event": "message",
        "data": json.dumps({
            "type": "complete",
            "result": result
        }, ensure_ascii=False)
    }

@app.post("/api/agent/solve")
async def agent_solve(request: AgentSolveRequest):
    return EventSourceResponse(
        agent_stream(request.problem, request.language)
    )

# 清空会话
@app.post("/api/session/clear")
async def session_clear(request: SessionClearRequest):
    return {"success": True, "message": "会话已清空"}

if __name__ == "__main__":
    import uvicorn
    print("AlgoMate Mock API 启动中...")
    print("http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
