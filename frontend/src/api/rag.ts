import type { RAGTokenEvent, SSEEvent } from "../types";

export interface TitleUpdateEvent {
    type: "title_update";
    title: string;
}

export async function* streamRAGChat(
    message: string, 
    sessionId: string
): AsyncGenerator<RAGTokenEvent | TitleUpdateEvent> {
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
                    const data: SSEEvent | TitleUpdateEvent = JSON.parse(line.slice(6));
                    if (data.type === "token" || data.type === "title_update") {
                        yield data;
                    }
                } catch (e) {
                    console.error("Failed to parse SSE data:", e);
                }
            }
        }
    }
}
