import { create } from "zustand";
import type { Message, Mode } from "../types";

interface ChatState {
    messages: Message[];
    mode: Mode;
    isLoading: boolean;
    agentProgress: number;
    agentStatus: string;
    sessionId: string;
    
    // Actions
    addMessage: (message: Message) => void;
    clearMessages: () => void;
    setMode: (mode: Mode) => void;
    setLoading: (loading: boolean) => void;
    updateLastMessage: (content: string) => void;
    updateLastMessageAgentResult: (agentResult: Message['agentResult']) => void;
    setAgentProgress: (progress: number) => void;
    setAgentStatus: (status: string) => void;
}

export const useChatStore = create<ChatState>((set) => ({
    messages: [],
    mode: "rag",
    isLoading: false,
    agentProgress: 0,
    agentStatus: "",
    sessionId: `session_${Date.now()}`,
    
    addMessage: (message) => 
        set((state) => ({ messages: [...state.messages, message] })),
    clearMessages: () => set({ messages: [] }),
    setMode: (mode) => set({ mode }),
    setLoading: (loading) => set({ isLoading: loading }),
    updateLastMessage: (content) =>
        set((state) => {
            const messages = [...state.messages];
            if (messages.length > 0 && messages[messages.length - 1].role === "assistant") {
                messages[messages.length - 1].content = content;
            }
            return { messages };
        }),
    updateLastMessageAgentResult: (agentResult) =>
        set((state) => {
            const messages = [...state.messages];
            if (messages.length > 0 && messages[messages.length - 1].role === "assistant") {
                messages[messages.length - 1].agentResult = agentResult;
            }
            return { messages };
        }),
    setAgentProgress: (progress) => set({ agentProgress: progress }),
    setAgentStatus: (status) => set({ agentStatus: status }),
}));
