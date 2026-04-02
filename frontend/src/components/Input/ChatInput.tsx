import { useState, useRef, useCallback } from "react";
import { Send, Loader2 } from "lucide-react";
import { useChatStore } from "../../stores/chatStore";
import { useConfigStore } from "../../stores/configStore";
import { streamRAGChat } from "../../api/rag";
import { streamAgentChat } from "../../api/agent";
import type { Message, AgentResult, SourceInfo, SourceSummary } from "../../types";

export function ChatInput() {
    const [input, setInput] = useState("");
    const inputRef = useRef<HTMLTextAreaElement>(null);
    
    const { 
        mode, 
        isLoading, 
        currentSessionId, 
        addMessage, 
        setLoading, 
        updateLastMessage,
        updateLastMessageAgentResult,
        setAgentProgress,
        setAgentStatus,
        updateSessionTitle,
        createSession
    } = useChatStore();
    
    const { language, maxIterations } = useConfigStore();

    const handleSubmit = useCallback(async () => {
        if (!input.trim() || isLoading) return;

        // Ensure we have a session
        let sessionId = currentSessionId;
        if (!sessionId) {
            console.log("[ChatInput] No session, creating new one...");
            sessionId = await createSession(mode);
            console.log("[ChatInput] Created session:", sessionId);
        }

        const userMessage: Message = {
            id: `msg_${Date.now()}`,
            role: "user",
            content: input.trim(),
            timestamp: Date.now(),
        };

        addMessage(userMessage);
        setInput("");
        setLoading(true);
        setAgentProgress(0);
        setAgentStatus("");

        // Add AI message placeholder
        const aiMessage: Message = {
            id: `msg_${Date.now() + 1}`,
            role: "assistant",
            content: "",
            timestamp: Date.now(),
        };
        addMessage(aiMessage);

        try {
            if (mode === "rag") {
                console.log("[ChatInput] Starting RAG chat, sessionId:", sessionId);
                // RAG streaming response
                let fullContent = "";
                let titleUpdated = false;
                let sources: SourceInfo[] | undefined;
                let summary: SourceSummary | undefined;
                
                for await (const event of streamRAGChat(userMessage.content, sessionId!)) {
                    console.log("[ChatInput] RAG event:", event.type);
                    if (event.type === "token") {
                        fullContent += event.content;
                        updateLastMessage(fullContent);
                    } else if (event.type === "source_info") {
                        // Store source information
                        sources = event.sources;
                        summary = event.summary;
                        console.log("[ChatInput] Received source_info:", {
                            sources: sources?.length,
                            summary
                        });
                    } else if (event.type === "title_update") {
                        console.log("[ChatInput] Received title_update:", event.title);
                        titleUpdated = true;
                        // Update session title when received from backend
                        await updateSessionTitle(sessionId!, event.title);
                        console.log("[ChatInput] Title updated successfully");
                    }
                }
                if (!titleUpdated) {
                    console.warn("[ChatInput] No title_update event received!");
                }
            } else {
                console.log("[ChatInput] Starting Agent chat, sessionId:", sessionId);
                // Agent streaming response
                let fullContent = "";
                let agentResult: AgentResult | undefined;
                let titleUpdated = false;

                for await (const event of streamAgentChat(
                    userMessage.content,
                    sessionId!,
                    language,
                    maxIterations
                )) {
                    console.log("[ChatInput] Agent event:", event.type);
                    switch (event.type) {
                        case "token":
                            fullContent += event.content;
                            updateLastMessage(fullContent);
                            break;
                        case "node_start":
                            setAgentStatus(event.status);
                            break;
                        case "progress":
                            setAgentProgress(event.value);
                            break;
                        case "complete":
                            agentResult = event.result;
                            // Set final_answer to message content
                            if (event.result?.final_answer) {
                                updateLastMessage(event.result.final_answer);
                            }
                            break;
                        case "title_update":
                            console.log("[ChatInput] Received title_update:", event.title);
                            titleUpdated = true;
                            // Update session title for agent mode
                            await updateSessionTitle(sessionId!, event.title);
                            console.log("[ChatInput] Title updated successfully");
                            break;
                    }
                }
                if (!titleUpdated) {
                    console.warn("[ChatInput] No title_update event received!");
                }

                if (agentResult) {
                    updateLastMessageAgentResult(agentResult);
                }
            }
        } catch (error) {
            console.error("[ChatInput] Chat error:", error);
            updateLastMessage("抱歉，发生了错误。请稍后重试。");
        } finally {
            setLoading(false);
            setAgentProgress(0);
            setAgentStatus("");
        }
    }, [
        input, 
        mode, 
        isLoading, 
        currentSessionId, 
        language, 
        maxIterations,
        addMessage, 
        setLoading, 
        updateLastMessage,
        updateLastMessageAgentResult,
        setAgentProgress,
        setAgentStatus,
        updateSessionTitle,
        createSession
    ]);

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    const placeholder = mode === "rag" 
        ? "输入您的问题..." 
        : "输入编程题目，Agent 将为您生成并执行代码...";

    return (
        <div className="p-4 bg-white/40 backdrop-blur-lg border-t border-white/40">
            <div className="max-w-4xl mx-auto">
                <div className="relative flex items-end gap-2">
                    <textarea
                        ref={inputRef}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder={placeholder}
                        disabled={isLoading}
                        rows={1}
                        className="glass-input flex-1 px-4 py-3 pr-12 resize-none min-h-[52px] max-h-[200px] text-gray-700 placeholder:text-gray-400 disabled:opacity-60"
                        style={{ height: 'auto' }}
                        onInput={(e) => {
                            const target = e.target as HTMLTextAreaElement;
                            target.style.height = 'auto';
                            target.style.height = `${Math.min(target.scrollHeight, 200)}px`;
                        }}
                    />
                    <button
                        onClick={handleSubmit}
                        disabled={!input.trim() || isLoading}
                        className={`flex-shrink-0 h-[52px] px-5 rounded-2xl font-medium text-white transition-all duration-200 flex items-center gap-2 ${
                            input.trim() && !isLoading
                                ? mode === "rag"
                                    ? "bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 hover:-translate-y-0.5"
                                    : "bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40 hover:-translate-y-0.5"
                                : "bg-gray-300 cursor-not-allowed"
                        }`}
                    >
                        {isLoading ? (
                            <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                            <>
                                <Send className="w-4 h-4" />
                                <span>发送</span>
                            </>
                        )}
                    </button>
                </div>
                <div className="mt-2 text-xs text-gray-400 text-center">
                    按 Enter 发送，Shift + Enter 换行
                </div>
            </div>
        </div>
    );
}
