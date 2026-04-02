/**
 * AlgoMate 前端类型定义
 * 
 * 包含所有业务类型、API事件类型和配置类型。
 */

/** 应用模式 */
export type Mode = "rag" | "agent";

/** 支持的编程语言 */
export type Language = "python" | "cpp" | "java";

/** 来源类型 */
export type SourceType = "vector_db" | "web_search";

/**
 * 消息对象
 */
export interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
    agentResult?: AgentResult;
    timestamp: number;
}

/**
 * Agent解题结果
 */
export interface AgentResult {
    final_answer?: string;
    generatedCode?: string;
    executionResult?: ExecutionResult;
    executionHistory?: ExecutionHistoryItem[];
    isSolved?: boolean;
    iteration_count?: number;
    language?: string;
}

/**
 * 代码执行结果
 */
export interface ExecutionResult {
    success: boolean;
    stdout: string;
    stderr: string;
    exitCode: number;
    executionTime: number;
    errorType: string | null;
}

/**
 * 执行历史记录项
 */
export interface ExecutionHistoryItem {
    iteration: number;
    code: string;
    result: ExecutionResult;
    fixes?: string;
}

// ============ SSE 事件类型 ============

/**
 * RAG Token事件 - 文本生成片段
 */
export interface RAGTokenEvent {
    type: "token";
    content: string;
}

/**
 * Agent节点开始事件
 */
export interface AgentNodeStartEvent {
    type: "node_start";
    node: string;
    status: string;
}

/**
 * Agent进度事件
 */
export interface AgentProgressEvent {
    type: "progress";
    value: number;
}

/**
 * Agent完成事件
 */
export interface AgentCompleteEvent {
    type: "complete";
    result: AgentResult;
}

/**
 * 标题更新事件
 */
export interface TitleUpdateEvent {
    type: "title_update";
    title: string;
}

/**
 * 来源信息
 */
export interface SourceInfo {
    type: SourceType;
    url?: string;
    title?: string;
    score?: number;
    doc_id?: string;
}

/**
 * 检索摘要
 */
export interface SourceSummary {
    vector_db_count: number;
    web_search_count: number;
    evaluation_score?: number;
    needs_web_search: boolean;
}

/**
 * 来源信息事件 - 增强RAG首先发送
 */
export interface SourceInfoEvent {
    type: "source_info";
    sources: SourceInfo[];
    summary: SourceSummary;
}

/**
 * SSE事件联合类型
 */
export type SSEEvent = 
    | RAGTokenEvent 
    | AgentNodeStartEvent 
    | AgentProgressEvent 
    | AgentCompleteEvent 
    | TitleUpdateEvent
    | SourceInfoEvent;

// ============ 配置类型 ============

/**
 * Agent配置
 */
export interface AgentConfig {
    language: Language;
    maxIterations: number;
}

// ============ 会话类型 ============

/**
 * 会话对象
 */
export interface ConversationSession {
    id: string;
    type: Mode;
    title: string;
    createdAt: string;
    updatedAt: string;
    messageCount: number;
    lastMessagePreview: string;
}

/**
 * 会话消息
 */
export interface ConversationMessage {
    id: string;
    sessionId: string;
    role: "user" | "assistant" | "system";
    content: string;
    timestamp: string;
    metadata?: {
        isRelevantToAlgorithm?: boolean;
        confidenceScore?: number;
        vectorStored?: boolean;
    };
}

// ============ RAG 相关类型 ============

/**
 * RAG检索来源
 */
export interface RAGSource {
    type: SourceType;
    content: string;
    url?: string;
    title?: string;
}

