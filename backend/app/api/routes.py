#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API 路由定义
"""
import json
import asyncio
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from .schemas import (
    RAGChatRequest,
    AgentSolveRequest,
    SessionClearRequest,
    ConfigResponse,
)
from app.core.session import session_manager


router = APIRouter()


# ============ 节点状态映射 ============
NODE_STATUS_MAP = {
    "analyze": "🔍 分析题目...",
    "generate_test_cases": "📝 生成测试用例...",
    "validate_test_cases": "✅ 验证测试用例...",
    "generate_code": "💻 生成代码...",
    "execute_code": "▶️ 执行代码...",
    "analyze_result": "📊 分析执行结果...",
    "fix_code": "🔧 修复代码...",
    "finish": "✨ 生成最终答案...",
}

NODE_PROGRESS_MAP = {
    "analyze": 10,
    "generate_test_cases": 20,
    "validate_test_cases": 30,
    "generate_code": 45,
    "execute_code": 60,
    "analyze_result": 75,
    "fix_code": 85,
    "finish": 100,
}


# ============ 健康检查 ============
@router.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok", "service": "AlgoMate API"}


# ============ RAG 问答 ============
async def rag_chat_stream(message: str, session_id: str) -> AsyncGenerator[dict, None]:
    """
    RAG 聊天流式生成器
    
    Args:
        message: 用户消息
        session_id: 会话ID
        
    Yields:
        SSE 事件字典
    """
    try:
        session = session_manager.get_session(session_id)
        rag_service = session["rag"]
        
        # 使用 RAG chain 的 stream 方法
        async for chunk in rag_service.chain.astream(
            {"input": message},
            config={"configurable": {"session_id": session_id}}
        ):
            if chunk:
                yield {
                    "event": "message",
                    "data": json.dumps({"type": "token", "content": chunk}, ensure_ascii=False)
                }
        
        # 发送完成事件
        yield {
            "event": "message",
            "data": json.dumps({"type": "done"}, ensure_ascii=False)
        }
        
    except Exception as e:
        yield {
            "event": "message",
            "data": json.dumps({"type": "error", "message": str(e)}, ensure_ascii=False)
        }


@router.post("/rag/chat")
async def rag_chat(request: RAGChatRequest):
    """
    RAG 问答（流式 SSE）
    
    Request Body:
        - message: 用户消息
        - session_id: 会话ID（可选，默认"default"）
    
    Response:
        SSE Stream:
        {"type": "token", "content": "..."}
        {"type": "done"}
    """
    return EventSourceResponse(
        rag_chat_stream(request.message, request.session_id),
        media_type="text/event-stream"
    )


# ============ Agent 解题 ============
def serialize_state_value(value) -> any:
    """序列化状态值，处理不可序列化的对象"""
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool, list, dict)):
        if isinstance(value, list):
            return [serialize_state_value(v) for v in value]
        if isinstance(value, dict):
            return {k: serialize_state_value(v) for k, v in value.items()}
        return value
    # 对于不可序列化的对象，转换为字符串
    return str(value)


async def agent_solve_stream(
    problem: str,
    language: str,
    max_iterations: int,
    session_id: str
) -> AsyncGenerator[dict, None]:
    """
    Agent 解题流式生成器
    
    Args:
        problem: 题目描述
        language: 编程语言
        max_iterations: 最大迭代次数
        session_id: 会话ID
        
    Yields:
        SSE 事件字典
    """
    try:
        # 获取或创建 Agent
        agent = session_manager.get_or_create_agent(session_id, max_iterations)
        
        # 发送开始事件
        yield {
            "event": "message",
            "data": json.dumps({
                "type": "node_start",
                "node": "start",
                "status": "🚀 开始解题..."
            }, ensure_ascii=False)
        }
        
        # 流式执行
        for event in agent.solve_stream(problem, language, session_id):
            for node_name, output in event.items():
                if node_name == "__end__":
                    continue
                
                # 发送节点开始事件
                status = NODE_STATUS_MAP.get(node_name, f"⏳ {node_name}...")
                yield {
                    "event": "message",
                    "data": json.dumps({
                        "type": "node_start",
                        "node": node_name,
                        "status": status
                    }, ensure_ascii=False)
                }
                
                # 发送进度事件
                progress = NODE_PROGRESS_MAP.get(node_name, 50)
                yield {
                    "event": "message",
                    "data": json.dumps({
                        "type": "progress",
                        "value": progress
                    }, ensure_ascii=False)
                }
                
                # 序列化输出
                serialized_output = {}
                if isinstance(output, dict):
                    serialized_output = {k: serialize_state_value(v) for k, v in output.items()}
                
                # 发送节点完成事件
                yield {
                    "event": "message",
                    "data": json.dumps({
                        "type": "node_complete",
                        "node": node_name,
                        "output": serialized_output
                    }, ensure_ascii=False)
                }
                
                # 小延迟，让前端有时间处理
                await asyncio.sleep(0.05)
        
        # 获取最终结果
        thread_config = {"configurable": {"thread_id": session_id}}
        final_state = agent.graph.get_state(thread_config)
        
        if final_state:
            result = {
                "final_answer": final_state.values.get("final_answer", ""),
                "is_solved": final_state.values.get("is_solved", False),
                "generatedCode": final_state.values.get("generated_code", ""),
                "language": final_state.values.get("language", language),
                "iteration_count": final_state.values.get("iteration_count", 0),
                "execution_history": serialize_state_value(
                    final_state.values.get("execution_history", [])
                ),
            }
        else:
            result = {"error": "未能获取最终状态"}
        
        # 保存结果到会话
        session = session_manager.get_session(session_id)
        session["agent_results"] = result
        
        # 发送完成事件
        yield {
            "event": "message",
            "data": json.dumps({
                "type": "complete",
                "result": result
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        yield {
            "event": "message",
            "data": json.dumps({
                "type": "error",
                "message": str(e),
                "detail": error_msg
            }, ensure_ascii=False)
        }


@router.post("/agent/solve")
async def agent_solve(request: AgentSolveRequest):
    """
    Agent 解题（流式 SSE）
    
    Request Body:
        - problem: 题目描述
        - language: 编程语言（python/cpp/java，默认python）
        - max_iterations: 最大迭代次数（1-10，默认5）
        - session_id: 会话ID（可选，默认"default"）
    
    Response:
        SSE Stream:
        {"type": "node_start", "node": "analyze", "status": "🔍 分析题目..."}
        {"type": "progress", "value": 15}
        {"type": "node_complete", "node": "analyze", "output": {...}}
        {"type": "complete", "result": {...}}
    """
    return EventSourceResponse(
        agent_solve_stream(
            request.problem,
            request.language,
            request.max_iterations,
            request.session_id
        ),
        media_type="text/event-stream"
    )


# ============ 清空会话 ============
@router.post("/session/clear")
async def session_clear(request: SessionClearRequest):
    """
    清空会话
    
    Request Body:
        - session_id: 会话ID（可选，默认"default"）
    
    Response:
        {"success": true, "message": "会话已清空"}
    """
    success = session_manager.clear_session(request.session_id)
    
    if success:
        return {
            "success": True,
            "message": f"会话 '{request.session_id}' 已清空"
        }
    else:
        return {
            "success": True,
            "message": f"会话 '{request.session_id}' 不存在或已清空"
        }


# ============ 获取配置 ============
@router.get("/config", response_model=ConfigResponse)
async def get_config():
    """
    获取配置信息
    
    Response:
        {
            "languages": ["python", "cpp", "java"],
            "max_iterations_range": [1, 10]
        }
    """
    return ConfigResponse()
