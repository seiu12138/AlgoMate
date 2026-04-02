/**
 * RAG API 调用模块
 * 
 * 提供标准RAG和增强RAG（带来源追踪）的流式API调用。
 */

import type { 
    RAGTokenEvent, 
    TitleUpdateEvent,
    SourceInfoEvent,
    SourceInfo,
    SourceSummary
} from "../types";

/** RAG事件类型联合 */
export type RAGEvent = RAGTokenEvent | TitleUpdateEvent;

/** 增强RAG事件类型联合 */
export type EnhancedRAGEvent = 
    | RAGTokenEvent 
    | TitleUpdateEvent 
    | SourceInfoEvent;

/**
 * 标准RAG流式对话
 * 
 * @param message - 用户消息
 * @param sessionId - 会话ID
 * @returns 异步生成器，产生RAG事件
 * 
 * @example
 * ```typescript
 * for await (const event of streamRAGChat("什么是DP?", "session-001")) {
 *   if (event.type === "token") {
 *     console.log(event.content);
 *   }
 * }
 * ```
 */
export async function* streamRAGChat(
    message: string, 
    sessionId: string
): AsyncGenerator<RAGEvent> {
    const response = await fetch("http://localhost:8000/api/rag/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, session_id: sessionId }),
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
        throw new Error("No reader available");
    }

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
            if (line.startsWith("data: ")) {
                try {
                    const data = JSON.parse(line.slice(6));
                    if (data.type === "token") {
                        yield data as RAGTokenEvent;
                    } else if (data.type === "title_update") {
                        yield data as TitleUpdateEvent;
                    }
                } catch (e) {
                    console.error("Failed to parse SSE data:", e);
                }
            }
        }
    }
}

/**
 * 增强RAG流式对话（带来源追踪）
 * 
 * @param message - 用户消息
 * @param sessionId - 会话ID
 * @param options - 可选配置
 * @param options.enableWebSearch - 是否启用网页搜索，默认true
 * @param options.enableSourceTagging - 是否启用来源标注，默认true
 * @returns 异步生成器，产生增强RAG事件（包含来源信息）
 * 
 * @example
 * ```typescript
 * for await (const event of streamEnhancedRAGChat("什么是DP?", "session-001")) {
 *   if (event.type === "source_info") {
 *     console.log("Sources:", event.sources);
 *     console.log("Summary:", event.summary);
 *   } else if (event.type === "token") {
 *     console.log(event.content);
 *   }
 * }
 * ```
 */
export async function* streamEnhancedRAGChat(
    message: string,
    sessionId: string,
    options: {
        enableWebSearch?: boolean;
        enableSourceTagging?: boolean;
    } = {}
): AsyncGenerator<EnhancedRAGEvent> {
    const { enableWebSearch = true, enableSourceTagging = true } = options;
    
    const response = await fetch("http://localhost:8000/api/rag/chat/enhanced", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            message,
            session_id: sessionId,
            enable_web_search: enableWebSearch,
            enable_source_tagging: enableSourceTagging,
        }),
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
        throw new Error("No reader available");
    }

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
            if (line.startsWith("data: ")) {
                try {
                    const data = JSON.parse(line.slice(6));
                    switch (data.type) {
                        case "source_info":
                            yield data as SourceInfoEvent;
                            break;
                        case "token":
                            yield data as RAGTokenEvent;
                            break;
                        case "title_update":
                            yield data as TitleUpdateEvent;
                            break;
                        case "done":
                        case "error":
                            yield data;
                            break;
                    }
                } catch (e) {
                    console.error("Failed to parse SSE data:", e);
                }
            }
        }
    }
}

export type { SourceInfo, SourceSummary };
