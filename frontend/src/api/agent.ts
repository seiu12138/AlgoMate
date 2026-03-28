import type { 
    RAGTokenEvent, 
    AgentNodeStartEvent, 
    AgentProgressEvent, 
    AgentCompleteEvent,
    TitleUpdateEvent,
    Language 
} from "../types";

export type AgentEvent = 
    | RAGTokenEvent 
    | AgentNodeStartEvent 
    | AgentProgressEvent 
    | AgentCompleteEvent
    | TitleUpdateEvent;

export async function* streamAgentChat(
    message: string,
    sessionId: string,
    language: Language,
    maxIterations: number
): AsyncGenerator<AgentEvent> {
    const response = await fetch("http://localhost:8000/api/agent/solve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
            problem: message, 
            session_id: sessionId,
            language,
            max_iterations: maxIterations
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
                    yield data as AgentEvent;
                } catch (e) {
                    console.error("Failed to parse SSE data:", e);
                }
            }
        }
    }
}
