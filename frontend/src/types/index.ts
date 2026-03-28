export type Mode = "rag" | "agent";
export type Language = "python" | "cpp" | "java";

export interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
    agentResult?: AgentResult;
    timestamp: number;
}

export interface AgentResult {
    final_answer?: string;
    generatedCode?: string;
    executionResult?: ExecutionResult;
    executionHistory?: ExecutionHistoryItem[];
    isSolved?: boolean;
    iteration_count?: number;
    language?: string;
}

export interface ExecutionResult {
    success: boolean;
    stdout: string;
    stderr: string;
    exitCode: number;
    executionTime: number;
    errorType: string | null;
}

export interface ExecutionHistoryItem {
    iteration: number;
    code: string;
    result: ExecutionResult;
    fixes?: string;
}

// SSE 事件类型
export interface RAGTokenEvent {
    type: "token";
    content: string;
}

export interface AgentNodeStartEvent {
    type: "node_start";
    node: string;
    status: string;
}

export interface AgentProgressEvent {
    type: "progress";
    value: number;
}

export interface AgentCompleteEvent {
    type: "complete";
    result: AgentResult;
}

export interface TitleUpdateEvent {
    type: "title_update";
    title: string;
}

export type SSEEvent = RAGTokenEvent | AgentNodeStartEvent | AgentProgressEvent | AgentCompleteEvent | TitleUpdateEvent;

// Agent 配置
export interface AgentConfig {
    language: Language;
    maxIterations: number;
}

// Conversation Session
export interface ConversationSession {
    id: string;
    type: Mode;
    title: string;
    createdAt: string;
    updatedAt: string;
    messageCount: number;
    lastMessagePreview: string;
}

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
