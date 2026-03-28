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
@router.get("/health", tags=["Health"])
async def health_check():
    """
    健康检查端点
    
    用于监控服务运行状态
    
    Returns:
        - status: "ok" 表示服务正常
        - service: 服务名称
    """
    return {"status": "ok", "service": "AlgoMate API"}


# ============ Session Management ============
@router.get("/sessions", response_model=SessionListResponse, tags=["Sessions"])
async def list_sessions(
    type: str = Query(None, description="Filter by session type: rag | agent")
):
    """
    获取所有会话列表
    
    获取所有会话的元数据列表，可按类型过滤
    
    - **type**: 可选，过滤会话类型 ("rag" 或 "agent")
    
    Returns:
        - sessions: 会话列表，按更新时间倒序排列
    """
    sessions = conversation_session_manager.list_sessions(session_type=type)
    return SessionListResponse(sessions=sessions)


@router.post("/sessions", response_model=CreateSessionResponse, tags=["Sessions"])
async def create_session(request: CreateSessionRequest):
    """
    创建新会话
    
    创建一个新的对话会话
    
    - **type**: 会话类型 ("rag" 或 "agent")
    - **title**: 可选，会话标题，默认 "New Conversation"
    
    Returns:
        - session: 新创建的会话信息
    """
    session = conversation_session_manager.create_session(
        session_type=request.type,
        title=request.title
    )
    return CreateSessionResponse(session=session)


@router.get("/sessions/{session_id}", response_model=SessionDetailResponse, tags=["Sessions"])
async def get_session(session_id: str):
    """
    获取会话详情（包含消息）
    
    获取指定会话的完整信息，包括所有消息
    
    - **session_id**: 路径参数，会话ID
    
    Returns:
        - session: 会话元数据
        - messages: 消息列表
        
    Raises:
        - 404: 会话不存在
    """
    session_data = conversation_session_manager.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionDetailResponse(
        session=session_data["session"],
        messages=session_data.get("messages", [])
    )


@router.delete("/sessions/{session_id}", tags=["Sessions"])
async def delete_session(session_id: str):
    """
    删除会话
    
    删除指定的会话及其所有消息
    
    - **session_id**: 路径参数，会话ID
    
    Returns:
        - success: 操作是否成功
        - message: 操作结果消息
    """
    conversation_session_manager.delete_session(session_id)
    return {"success": True, "message": f"Session '{session_id}' deleted"}


@router.patch("/sessions/{session_id}", tags=["Sessions"])
async def update_session(session_id: str, request: UpdateSessionRequest):
    """
    更新会话标题
    
    修改指定会话的标题
    
    - **session_id**: 路径参数，会话ID
    - **title**: 新标题
    
    Response:
        {"success": true, "message": "..."}
    """
    session_data = conversation_session_manager.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    conversation_session_manager.update_title(session_id, request.title)
    return {"success": True, "message": f"Session '{session_id}' title updated"}


@router.post("/sessions/{session_id}/summarize", response_model=SummaryResponse, tags=["Sessions"])
async def generate_summary_endpoint(session_id: str):
    """
    生成会话摘要标题
    
    基于会话的第一条消息自动生成标题
    
    - **session_id**: 路径参数，会话ID
    
    Returns:
        - title: 生成的标题
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
    
    # Use truncated first message as fallback
    title = first_message[:30] + "..." if len(first_message) > 30 else first_message
    return SummaryResponse(title=title)


# ============ RAG 问答（增强版） ============
async def rag_chat_stream_enhanced(
    message: str, 
    session_id: str,
    conversation_rag=None,
    rag_service=None
) -> AsyncGenerator[dict, None]:
    """
    RAG 聊天流式生成器（增强版，支持会话持久化）
    
    Args:
        message: 用户消息
        session_id: 会话ID
        conversation_rag: ConversationRAG实例
        rag_service: RAG服务实例
        
    Yields:
        SSE 事件字典
    """
    try:
        # 1. Validate session exists
        session_data = conversation_session_manager.get_session(session_id)
        if not session_data:
            yield {
                "event": "message",
                "data": json.dumps({"type": "error", "message": "Session not found"}, ensure_ascii=False)
            }
            return
        
        # Check if this is the first message (for auto-title generation)
        is_first_message = session_data["session"]["messageCount"] == 0
        
        # 2. Store user message
        if conversation_rag:
            await conversation_rag.process_message(
                session_id=session_id,
                message=message,
                role="user",
                skip_vector_store=True  # Don't store user messages in vector DB
            )
        
        # 3. Get enhanced context (vector DB + session history)
        enhanced_context = ""
        if conversation_rag:
            enhanced_context = await conversation_rag.get_enhanced_context(
                query=message,
                session_id=session_id,
                k=3,
                max_history=5
            )
        
        # 4. Generate response with context using RAG service
        if rag_service:
            # Use existing RAG service with enhanced context
            full_response = ""
            async for chunk in rag_service.chain.astream(
                {"input": message, "context": enhanced_context},
                config={"configurable": {"session_id": session_id}}
            ):
                if chunk:
                    full_response += chunk
                    yield {
                        "event": "message",
                        "data": json.dumps({"type": "token", "content": chunk}, ensure_ascii=False)
                    }
            
            # 5. Store assistant response with relevance check
            if conversation_rag:
                await conversation_rag.process_message(
                    session_id=session_id,
                    message=full_response,
                    role="assistant"
                )
            
            # 6. Auto-generate summary if first message
            if is_first_message:
                try:
                    # Try to use LLM for summary if available
                    if conversation_rag:
                        summary = await conversation_rag.generate_summary(message)
                    else:
                        # Fallback: truncate first message
                        summary = message[:30] + "..." if len(message) > 30 else message
                    
                    conversation_session_manager.update_title(session_id, summary)
                    yield {
                        "event": "message",
                        "data": json.dumps({"type": "title_update", "title": summary}, ensure_ascii=False)
                    }
                except Exception as e:
                    print(f"Warning: Failed to generate summary: {e}")
        else:
            # Fallback: simple response without RAG
            # Still generate title if first message
            if is_first_message:
                try:
                    summary = message[:30] + "..." if len(message) > 30 else message
                    conversation_session_manager.update_title(session_id, summary)
                    yield {
                        "event": "message",
                        "data": json.dumps({"type": "title_update", "title": summary}, ensure_ascii=False)
                    }
                except Exception as e:
                    print(f"Warning: Failed to generate summary: {e}")
            
            yield {
                "event": "message",
                "data": json.dumps({"type": "error", "message": "RAG service not available"}, ensure_ascii=False)
            }
        
        # Send completion event
        yield {
            "event": "message",
            "data": json.dumps({"type": "done"}, ensure_ascii=False)
        }
        
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        yield {
            "event": "message",
            "data": json.dumps({"type": "error", "message": str(e), "detail": error_msg}, ensure_ascii=False)
        }


@router.post("/rag/chat", tags=["RAG"])
async def rag_chat(request: RAGChatRequest):
    """
    RAG 问答（流式 SSE）
    
    基于检索增强生成的知识问答
    
    ## 功能
    - 向量检索相关知识
    - 会话持久化
    - 首次对话自动生成标题
    
    ## 请求参数
    - **message**: 用户问题
    - **session_id**: 会话ID（必需）
    
    ## 响应 (SSE 流)
    - `{"type": "token", "content": "..."}` - 生成的文本片段
    - `{"type": "title_update", "title": "..."}` - 首次对话时发送
    - `{"type": "done"}` - 完成标记
    
    ## 示例
    ```python
    import requests
    
    response = requests.post(
        "http://localhost:8000/api/rag/chat",
        json={"message": "什么是动态规划？", "session_id": "xxx"},
        stream=True
    )
    
    for line in response.iter_lines():
        if line.startswith(b"data: "):
            data = json.loads(line[6:])
            print(data)
    ```
    """
    try:
        # Import here to avoid circular dependencies
        from app.rag.conversation_rag import get_conversation_rag
        
        # Get RAG service from session manager
        session = session_manager.get_session(request.session_id)
        rag_service = session.get("rag") if session else None
        
        # Get ConversationRAG instance
        try:
            conversation_rag = get_conversation_rag()
        except ValueError:
            # Initialize if not exists (need vector_store and llm)
            if rag_service:
                from app.rag.conversation_rag import ConversationRAG
                # Extract vector_store and llm from existing RAG service
                vector_store = getattr(rag_service, 'vector_service', None)
                llm = getattr(rag_service, 'chat_model', None)
                if vector_store and llm:
                    conversation_rag = ConversationRAG(vector_store, llm)
                else:
                    conversation_rag = None
            else:
                conversation_rag = None
        
        return EventSourceResponse(
            rag_chat_stream_enhanced(
                request.message, 
                request.session_id,
                conversation_rag=conversation_rag,
                rag_service=rag_service
            ),
            media_type="text/event-stream"
        )
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)


# ============ Agent 解题（增强版） ============
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


async def agent_solve_stream_enhanced(
    problem: str,
    language: str,
    max_iterations: int,
    session_id: str,
    enhanced_agent=None
) -> AsyncGenerator[dict, None]:
    """
    Agent 解题流式生成器（增强版，支持会话持久化）
    
    Args:
        problem: 题目描述
        language: 编程语言
        max_iterations: 最大迭代次数
        session_id: 会话ID
        enhanced_agent: EnhancedAgent实例
        
    Yields:
        SSE 事件字典
    """
    try:
        # 1. Validate session
        session_data = conversation_session_manager.get_session(session_id)
        if not session_data:
            yield {
                "event": "message",
                "data": json.dumps({"type": "error", "message": "Session not found"}, ensure_ascii=False)
            }
            return
        
        # Check if this is the first message (for auto-title generation)
        is_first_message = session_data["session"]["messageCount"] == 0
        
        # 2. Store user message
        conversation_session_manager.add_message(session_id, {
            "role": "user",
            "content": problem
        })
        
        # 3. Get RAG context if available
        rag_context = ""
        if enhanced_agent and enhanced_agent.conversation_rag:
            try:
                rag_context = await enhanced_agent.conversation_rag.get_enhanced_context(
                    query=problem,
                    session_id=session_id,
                    k=3,
                    max_history=5
                )
            except Exception as e:
                print(f"Warning: Failed to get RAG context: {e}")
        
        # 4. Enhance problem with context
        if rag_context:
            enhanced_problem = f"""{problem}

[Additional Context from Knowledge Base]
{rag_context}
"""
        else:
            enhanced_problem = problem
        
        # 5. Get or create Agent
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
        
        # 6. Stream execution
        for event in agent.solve_stream(enhanced_problem, language, session_id):
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
        
        # 7. Get final result
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
        
        # 8. Store assistant response
        conversation_session_manager.add_message(session_id, {
            "role": "assistant",
            "content": result.get("final_answer", ""),
            "metadata": {
                "generatedCode": result.get("generatedCode"),
                "executionResult": result.get("execution_history", [])[-1] if result.get("execution_history") else None,
                "isSolved": result.get("is_solved"),
                "iterationCount": result.get("iteration_count"),
                "language": language
            }
        })
        
        # 9. Auto-generate title if first message
        if is_first_message:
            try:
                # Simple title generation (first 30 chars)
                title = problem[:30] + "..." if len(problem) > 30 else problem
                conversation_session_manager.update_title(session_id, title)
                yield {
                    "event": "message",
                    "data": json.dumps({"type": "title_update", "title": title}, ensure_ascii=False)
                }
            except Exception as e:
                print(f"Warning: Failed to generate title: {e}")
        
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


@router.post("/agent/solve", tags=["Agent"])
async def agent_solve(request: AgentSolveRequest):
    """
    Agent 解题（流式 SSE）
    
    智能 Agent 自动分析题目、生成代码、执行测试、修复错误
    
    ## 功能
    - 自动分析算法题目
    - 生成可执行代码 (Python/C++/Java)
    - 自动生成测试用例
    - 自动执行并验证
    - 自动修复错误 (ReAct 循环)
    - 会话持久化
    
    ## 请求参数
    - **problem**: 题目描述
    - **language**: 编程语言 ("python", "cpp", "java")，默认 "python"
    - **max_iterations**: 最大迭代次数 (1-10)，默认 5
    - **session_id**: 会话ID（必需）
    
    ## 响应 (SSE 流)
    - `{"type": "node_start", "node": "analyze", "status": "..."}` - 节点开始
    - `{"type": "progress", "value": 15}` - 进度更新 (0-100)
    - `{"type": "node_complete", "node": "...", "output": {...}}` - 节点完成
    - `{"type": "title_update", "title": "..."}` - 首次对话时发送
    - `{"type": "complete", "result": {...}}` - 最终完成结果
    - `{"type": "error", "message": "..."}` - 错误信息
    
    ## 执行流程
    1. **analyze** - 分析题目
    2. **generate_test_cases** - 生成测试用例
    3. **validate_test_cases** - 验证测试用例
    4. **generate_code** - 生成代码
    5. **execute_code** - 执行代码
    6. **analyze_result** - 分析结果
    7. **fix_code** - 修复代码 (如需要)
    8. **finish** - 生成最终答案
    
    ## 示例
    ```python
    import requests
    
    response = requests.post(
        "http://localhost:8000/api/agent/solve",
        json={
            "problem": "两数之和：给定数组 nums 和 target...",
            "language": "python",
            "max_iterations": 5,
            "session_id": "xxx"
        },
        stream=True
    )
    
    for line in response.iter_lines():
        if line.startswith(b"data: "):
            data = json.loads(line[6:])
            print(data)
    ```
    """
    return EventSourceResponse(
        agent_solve_stream_enhanced(
            request.problem,
            request.language,
            request.max_iterations,
            request.session_id,
            enhanced_agent=None  # Will be initialized in the stream function
        ),
        media_type="text/event-stream"
    )


# ============ 清空会话 ============
@router.post("/session/clear", tags=["Sessions"])
async def session_clear(request: SessionClearRequest):
    """
    清空会话
    
    清空指定会话的运行时状态（不影响持久化存储的会话）
    
    - **session_id**: 会话ID，默认 "default"
    
    Returns:
        - success: 操作是否成功
        - message: 操作结果消息
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
@router.get("/config", tags=["System"])
async def get_config():
    """
    获取配置信息
    
    获取系统支持的编程语言和配置范围
    
    Returns:
        - languages: 支持的编程语言列表
        - max_iterations_range: 最大迭代次数范围 [min, max]
    """
    return {
        "languages": ["python", "cpp", "java"],
        "max_iterations_range": [1, 10]
    }
