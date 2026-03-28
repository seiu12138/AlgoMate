#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API Pydantic 模型定义
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal, List


class RAGChatRequest(BaseModel):
    """RAG 聊天请求"""
    message: str = Field(..., description="用户消息")
    session_id: str = Field(default="default", description="会话ID")


class AgentSolveRequest(BaseModel):
    """Agent 解题请求"""
    problem: str = Field(..., description="题目描述")
    language: Literal["python", "cpp", "java"] = Field(default="python", description="编程语言")
    max_iterations: int = Field(default=5, ge=1, le=10, description="最大迭代次数")
    session_id: str = Field(default="default", description="会话ID")


class SessionClearRequest(BaseModel):
    """清空会话请求"""
    session_id: str = Field(default="default", description="会话ID")


class ConfigResponse(BaseModel):
    """配置响应"""
    languages: List[str] = Field(default=["python", "cpp", "java"], description="支持的编程语言")
    max_iterations_range: List[int] = Field(default=[1, 10], description="最大迭代次数范围")


class SSEMessage(BaseModel):
    """SSE 消息基类"""
    type: str = Field(..., description="消息类型")


class SSEToken(SSEMessage):
    """SSE Token 消息"""
    type: Literal["token"] = "token"
    content: str = Field(..., description="token内容")


class SSEDone(SSEMessage):
    """SSE 完成消息"""
    type: Literal["done"] = "done"


class SSENodeStart(SSEMessage):
    """Agent 节点开始消息"""
    type: Literal["node_start"] = "node_start"
    node: str = Field(..., description="节点名称")
    status: str = Field(..., description="状态描述")


class SSENodeComplete(SSEMessage):
    """Agent 节点完成消息"""
    type: Literal["node_complete"] = "node_complete"
    node: str = Field(..., description="节点名称")
    output: dict = Field(default_factory=dict, description="节点输出")


class SSEProgress(SSEMessage):
    """进度更新消息"""
    type: Literal["progress"] = "progress"
    value: int = Field(..., ge=0, le=100, description="进度百分比")


class SSEComplete(SSEMessage):
    """Agent 完成消息"""
    type: Literal["complete"] = "complete"
    result: dict = Field(default_factory=dict, description="最终结果")


class SSEError(SSEMessage):
    """错误消息"""
    type: Literal["error"] = "error"
    message: str = Field(..., description="错误信息")


# ============ Session Management Models ============


class CreateSessionRequest(BaseModel):
    """创建会话请求"""
    type: Literal["rag", "agent"] = Field(..., description="会话类型: rag 或 agent")
    title: Optional[str] = Field(default=None, description="会话标题（可选）")


class CreateSessionResponse(BaseModel):
    """创建会话响应"""
    session: dict = Field(..., description="会话信息")


class SessionListResponse(BaseModel):
    """会话列表响应"""
    sessions: List[dict] = Field(default_factory=list, description="会话列表")


class SessionDetailResponse(BaseModel):
    """会话详情响应"""
    session: dict = Field(..., description="会话元数据")
    messages: List[dict] = Field(default_factory=list, description="消息列表")


class UpdateSessionRequest(BaseModel):
    """更新会话请求"""
    title: str = Field(..., description="新标题")


class SummaryResponse(BaseModel):
    """生成摘要响应"""
    title: str = Field(..., description="生成的标题")
