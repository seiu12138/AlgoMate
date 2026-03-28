#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API 路由定义
"""
import json
import asyncio
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from .schemas import (
    RAGChatRequest,
    AgentSolveRequest,
    SessionClearRequest,
    CreateSessionRequest,
    UpdateSessionRequest,
    CreateSessionResponse,
    SessionListResponse,
    SessionDetailResponse,
    SummaryResponse,
)
from app.core.session import session_manager
from app.core.session_manager import get_session_manager


router = APIRouter()

# Session manager instance
conversation_session_manager = get_session_manager()


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


# ============ Session Management ============
@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    type: str = Query(None, description="Filter by session type: rag | agent")
):
    """
    获取所有会话列表
    
    Query Parameters:
        - type: 可选，过滤会话类型 ("rag" 或 "agent")
    
    Response:
        {"sessions": [session1, session2, ...]}
    """
    sessions = conversation_session_manager.list_sessions(session_type=type)
    return SessionListResponse(sessions=sessions)


@router.post("/sessions", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest):
    """
    创建新会话
    
    Request Body:
        - type: 会话类型 ("rag" 或 "agent")
        - title: 可选，会话标题
    
    Response:
        {"session": {"id": "...", "type": "...", "title": "...", ...}}
    """
    session = conversation_session_manager.create_session(
        session_type=request.type,
        title=request.title
    )
    return CreateSessionResponse(session=session)


@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
async def get_session(session_id: str):
    """
    获取会话详情（包含消息）
    
    Path Parameters:
        - session_id: 会话ID
    
    Response:
        {"session": {...}, "messages": [...]}
    """
    session_data = conversation_session_manager.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionDetailResponse(
        session=session_data["session"],
        messages=session_data.get("messages", [])
    )


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    删除会话
    
    Path Parameters:
        - session_id: 会话ID
    
    Response:
        {"success": true, "message": "..."}
    """
    conversation_session_manager.delete_session(session_id)
    return {"success": True, "message": f"Session '{session_id}' deleted"}


@router.patch("/sessions/{session_id}")
async def update_session(session_id: str, request: UpdateSessionRequest):
    """
    更新会话标题
    
    Path Parameters:
        - session_id: 会话ID
    
    Request Body:
        - title: 新标题
    
    Response:
        {"success": true, "message": "..."}
    """
    session_data = conversation_session_manager.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    conversation_session_manager.update_title(session_id, request.title)
    return {"success": True, "message": f"Session '{session_id}' title updated"}


@router.post("/sessions/{session_id}/summarize", response_model=SummaryResponse)
async def generate_summary(session_id: str):
    """
    生成会话摘要标题
    
    Path Parameters:
        - session_id: 会话ID
    
    Response:
        {"title": "生成的标题"}
    """
    session_data = conversation_session_manager.get_session(session_id)
    if not session_data or not session_data.get("messages"):
        return SummaryResponse(title="New Conversation")
    
    # Get first user message for summary
    first_message = None
    for msg in session_data["messages"]:
        if msg.get("role") == "user":
            first_message = msg.get("content", "")
            break
    
    if not first_message:
        return SummaryResponse(title="New Conversation")
    
    # TODO: Use LLM to generate summary
    # For now, use truncated first message
    title = first_message[:30] + "..." if len(first_message) > 30 else first_message
    return SummaryResponse(title=title)


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
        
        # Use RAG chain's stream method
        async for chunk in rag_service.chain.astream(
            {"input": message},
            config={"configurable": {"session_id": session_id}}
        ):
            if chunk:
                yield {
                    "event": "message",
                    "data": json.dumps({"type": "token", "content": chunk}, ensure_ascii=False)
                }
        
        # Send completion event
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
        # Get or create Agent
        agent = session_manager.get_or_create_agent(session_id, max_iterations)
        
        # Send start event
        yield {
            "event": "message",
            "data": json.dumps({
                "type": "node_start",
                "node": "start",
                "status": "🚀 开始解题..."
            }, ensure_ascii=False)
        }
        
        # Stream execution
        for event in agent.solve_stream(problem, language, session_id):
            for node_name, output in event.items():
                if node_name == "__end__":
                    continue
                
                # Send node start event
                status = NODE_STATUS_MAP.get(node_name, f"⏳ {node_name}...")
                yield {
                    "event": "message",
                    "data": json.dumps({
                        "type": "node_start",
                        "node": node_name,
                        "status": status
                    }, ensure_ascii=False)
                }
                
                # Send progress event
                progress = NODE_PROGRESS_MAP.get(node_name, 50)
                yield {
                    "event": "message",
                    "data": json.dumps({
                        "type": "progress",
                        "value": progress
                    }, ensure_ascii=False)
                }
                
                # Serialize output
                serialized_output = {}
                if isinstance(output, dict):
                    serialized_output = {k: serialize_state_value(v) for k, v in output.items()}
                
                # Send node complete event
                yield {
                    "event": "message",
                    "data": json.dumps({
                        "type": "node_complete",
                        "node": node_name,
                        "output": serialized_output
                    }, ensure_ascii=False)
                }
                
                # Small delay for frontend processing
                await asyncio.sleep(0.05)
        
        # Get final result
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
        
        # Save result to session
        session = session_manager.get_session(session_id)
        session["agent_results"] = result
        
        # Send completion event
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
@router.get("/config")
async def get_config():
    """
    获取配置信息
    
    Response:
        {
            "languages": ["python", "cpp", "java"],
            "max_iterations_range": [1, 10]
        }
    """
    return {
        "languages": ["python", "cpp", "java"],
        "max_iterations_range": [1, 10]
    }
