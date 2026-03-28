import type { RAGTokenEvent, TitleUpdateEvent } from "../types";

export type RAGEvent = RAGTokenEvent | TitleUpdateEvent;

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
