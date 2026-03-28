import type { Mode } from "../types";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export interface CreateSessionRequest {
    type: Mode;
    title?: string;
}

export interface CreateSessionResponse {
    session: {
        id: string;
        type: Mode;
        title: string;
        createdAt: string;
        updatedAt: string;
        messageCount: number;
        lastMessagePreview: string;
    };
}

export interface SessionListResponse {
    sessions: Array<{
        id: string;
        type: Mode;
        title: string;
        createdAt: string;
        updatedAt: string;
        messageCount: number;
        lastMessagePreview: string;
    }>;
}

export interface SessionDetailResponse {
    session: {
        id: string;
        type: Mode;
        title: string;
        createdAt: string;
        updatedAt: string;
        messageCount: number;
        lastMessagePreview: string;
    };
    messages: Array<{
        id: string;
        sessionId: string;
        role: "user" | "assistant" | "system";
        content: string;
        timestamp: string;
        metadata?: any;
    }>;
}

export const sessionAPI = {
    async createSession(type: Mode, title?: string): Promise<CreateSessionResponse> {
        const response = await fetch(`${API_BASE}/sessions`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ type, title }),
        });
        
        if (!response.ok) {
            throw new Error(`Failed to create session: ${response.statusText}`);
        }
        
        return response.json();
    },
    
    async listSessions(type?: Mode): Promise<SessionListResponse> {
        const url = type 
            ? `${API_BASE}/sessions?type=${type}` 
            : `${API_BASE}/sessions`;
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`Failed to list sessions: ${response.statusText}`);
        }
        
        return response.json();
    },
    
    async getSession(sessionId: string): Promise<SessionDetailResponse> {
        const response = await fetch(`${API_BASE}/sessions/${sessionId}`);
        
        if (!response.ok) {
            throw new Error(`Failed to get session: ${response.statusText}`);
        }
        
        return response.json();
    },
    
    async deleteSession(sessionId: string): Promise<void> {
        const response = await fetch(`${API_BASE}/sessions/${sessionId}`, {
            method: "DELETE",
        });
        
        if (!response.ok) {
            throw new Error(`Failed to delete session: ${response.statusText}`);
        }
    },
    
    async updateSession(sessionId: string, title: string): Promise<void> {
        const response = await fetch(`${API_BASE}/sessions/${sessionId}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title }),
        });
        
        if (!response.ok) {
            throw new Error(`Failed to update session: ${response.statusText}`);
        }
    },
    
    async generateSummary(sessionId: string): Promise<{ title: string }> {
        const response = await fetch(`${API_BASE}/sessions/${sessionId}/summarize`, {
            method: "POST",
        });
        
        if (!response.ok) {
            throw new Error(`Failed to generate summary: ${response.statusText}`);
        }
        
        return response.json();
    },
};
