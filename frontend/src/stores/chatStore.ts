import { create } from "zustand";
import type { Message, Mode, ConversationSession } from "../types";
import { sessionAPI } from "../services/sessionAPI";

interface ChatState {
    // Messages
    messages: Message[];
    mode: Mode;
    isLoading: boolean;
    agentProgress: number;
    agentStatus: string;
    
    // Session management
    currentSessionId: string | null;
    sessions: ConversationSession[];
    isLoadingSessions: boolean;
    
    // Actions
    addMessage: (message: Message) => void;
    clearMessages: () => void;
    setMode: (mode: Mode) => void;
    setLoading: (loading: boolean) => void;
    updateLastMessage: (content: string) => void;
    updateLastMessageAgentResult: (agentResult: Message['agentResult']) => void;
    setAgentProgress: (progress: number) => void;
    setAgentStatus: (status: string) => void;
    
    // Session actions
    createSession: (type: Mode) => Promise<string>;
    loadSession: (sessionId: string) => Promise<void>;
    deleteSession: (sessionId: string) => Promise<void>;
    loadSessions: (type?: Mode) => Promise<void>;
    loadRecentSession: (type: Mode) => Promise<void>;
    updateSessionTitle: (sessionId: string, title: string) => Promise<void>;
    setCurrentSessionId: (sessionId: string | null) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
    // Initial state
    messages: [],
    mode: "rag",
    isLoading: false,
    agentProgress: 0,
    agentStatus: "",
    currentSessionId: null,
    sessions: [],
    isLoadingSessions: false,
    
    // Basic actions
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
    setCurrentSessionId: (sessionId) => set({ currentSessionId: sessionId }),
    
    // Session actions
    createSession: async (type: Mode) => {
        try {
            // Check for empty session to reuse
            const { sessions } = get();
            const emptySession = sessions.find(
                s => s.type === type && s.messageCount === 0
            );
            
            if (emptySession) {
                // Reuse existing empty session
                set({
                    currentSessionId: emptySession.id,
                    messages: [],
                });
                return emptySession.id;
            }
            
            // Create new session
            const response = await sessionAPI.createSession(type);
            const session = response.session;
            set((state) => ({
                currentSessionId: session.id,
                sessions: [session, ...state.sessions],
                messages: [],
            }));
            return session.id;
        } catch (error) {
            console.error("Failed to create session:", error);
            throw error;
        }
    },
    
    loadSession: async (sessionId: string) => {
        try {
            set({ isLoadingSessions: true });
            const response = await sessionAPI.getSession(sessionId);
            
            // If no messages, clear current messages
            if (!response.messages || response.messages.length === 0) {
                set({
                    currentSessionId: sessionId,
                    messages: [],
                    mode: response.session.type,
                    isLoadingSessions: false,
                });
                return;
            }
            
            // Convert backend messages to frontend format
            const messages: Message[] = response.messages.map((msg: any) => ({
                id: msg.id,
                role: msg.role === "assistant" ? "assistant" : "user",
                content: msg.content,
                timestamp: new Date(msg.timestamp).getTime(),
                agentResult: msg.metadata,
            }));
            
            set({
                currentSessionId: sessionId,
                messages,
                mode: response.session.type,
                isLoadingSessions: false,
            });
        } catch (error) {
            console.error("Failed to load session:", error);
            set({ isLoadingSessions: false });
            throw error;
        }
    },
    
    deleteSession: async (sessionId: string) => {
        try {
            await sessionAPI.deleteSession(sessionId);
            set((state) => {
                const newSessions = state.sessions.filter(s => s.id !== sessionId);
                const newState: any = { sessions: newSessions };
                
                // If deleted current session, clear it
                if (state.currentSessionId === sessionId) {
                    newState.currentSessionId = null;
                    newState.messages = [];
                }
                
                return newState;
            });
        } catch (error) {
            console.error("Failed to delete session:", error);
            throw error;
        }
    },
    
    loadSessions: async (type?: Mode) => {
        try {
            set({ isLoadingSessions: true });
            const response = await sessionAPI.listSessions(type);
            set({ 
                sessions: response.sessions,
                isLoadingSessions: false,
            });
        } catch (error) {
            console.error("Failed to load sessions:", error);
            set({ isLoadingSessions: false });
        }
    },
    
    loadRecentSession: async (type: Mode) => {
        const { sessions, createSession } = get();
        const recentSession = sessions.find(s => s.type === type);
        
        if (recentSession) {
            await get().loadSession(recentSession.id);
        } else {
            await createSession(type);
        }
    },
    
    updateSessionTitle: async (sessionId: string, title: string) => {
        try {
            await sessionAPI.updateSession(sessionId, title);
            set((state) => ({
                sessions: state.sessions.map(s =>
                    s.id === sessionId ? { ...s, title } : s
                ),
            }));
        } catch (error) {
            console.error("Failed to update session title:", error);
            throw error;
        }
    },
}));
