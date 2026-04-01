import type { Mode } from "../types";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

// Track backend availability to prevent repeated failed requests
let isBackendAvailable = true;
let lastBackendCheck = 0;
const BACKEND_CHECK_INTERVAL = 5000; // 5 seconds when available
const BACKEND_RETRY_INTERVAL = 1000; // 1 second when unavailable (faster retry)
let retryAttempt = 0;
const MAX_RETRY_INTERVAL = 10000; // Max 10 seconds

async function checkBackendAvailability(): Promise<boolean> {
    const now = Date.now();
    const cacheInterval = isBackendAvailable ? BACKEND_CHECK_INTERVAL : Math.min(BACKEND_RETRY_INTERVAL * (2 ** retryAttempt), MAX_RETRY_INTERVAL);
    
    if (now - lastBackendCheck < cacheInterval) {
        return isBackendAvailable;
    }
    
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 2000);
        
        const response = await fetch(`${API_BASE}/health`, {
            method: "GET",
            signal: controller.signal,
        });
        
        clearTimeout(timeoutId);
        
        const wasAvailable = isBackendAvailable;
        isBackendAvailable = response.ok;
        lastBackendCheck = now;
        
        // Reset retry counter on success
        if (isBackendAvailable) {
            retryAttempt = 0;
        } else {
            retryAttempt = Math.min(retryAttempt + 1, 5); // Cap at 5 (32 seconds)
        }
        
        // Log state change
        if (!wasAvailable && isBackendAvailable) {
            console.log("[sessionAPI] Backend is now available");
        } else if (wasAvailable && !isBackendAvailable) {
            console.warn("[sessionAPI] Backend became unavailable");
        }
        
        return isBackendAvailable;
    } catch {
        const wasAvailable = isBackendAvailable;
        isBackendAvailable = false;
        lastBackendCheck = now;
        retryAttempt = Math.min(retryAttempt + 1, 5);
        
        if (wasAvailable) {
            console.warn("[sessionAPI] Backend became unavailable");
        }
        
        return false;
    }
}

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
        // Check backend availability first
        if (!await checkBackendAvailability()) {
            console.warn("[sessionAPI] Backend not available, returning empty sessions");
            return { sessions: [] };
        }
        
        const url = type 
            ? `${API_BASE}/sessions?type=${type}` 
            : `${API_BASE}/sessions`;
        
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000);
            
            const response = await fetch(url, {
                signal: controller.signal,
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`Failed to list sessions: ${response.statusText}`);
            }
            
            return response.json();
        } catch (error) {
            if (error instanceof Error) {
                if (error.name === "AbortError") {
                    console.warn("[sessionAPI] Request timeout");
                } else if ((error as any).code === "ECONNREFUSED" || error.message.includes("fetch")) {
                    console.warn("[sessionAPI] Connection refused, backend may be down");
                    isBackendAvailable = false;
                }
            }
            // Return empty sessions on error
            return { sessions: [] };
        }
    },
    
    async getSession(sessionId: string): Promise<SessionDetailResponse | null> {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000);
            
            const response = await fetch(`${API_BASE}/sessions/${sessionId}`, {
                signal: controller.signal,
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                if (response.status === 404) {
                    return null;
                }
                throw new Error(`Failed to get session: ${response.statusText}`);
            }
            
            return response.json();
        } catch (error) {
            console.warn(`[sessionAPI] Failed to get session ${sessionId}:`, error);
            return null;
        }
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
    
    // Check if backend is available
    isBackendAvailable: () => isBackendAvailable,
    checkBackendAvailability,
};
