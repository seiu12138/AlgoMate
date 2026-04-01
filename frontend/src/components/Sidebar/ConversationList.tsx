import { useState, useEffect, useCallback } from "react";
import { Plus, Loader2, AlertCircle, RefreshCw } from "lucide-react";
import { ConversationCard } from "./ConversationCard";
import { useChatStore } from "../../stores/chatStore";
import { sessionAPI } from "../../services/sessionAPI";
import type { Mode } from "../../types";

interface ConversationListProps {
    mode: Mode;
}

export function ConversationList({ mode }: ConversationListProps) {
    const [error, setError] = useState<string | null>(null);
    const [isCreating, setIsCreating] = useState(false);
    const [isBackendReady, setIsBackendReady] = useState(true);
    const [retryCount, setRetryCount] = useState(0);
    
    const {
        sessions,
        currentSessionId,
        isLoadingSessions,
        loadSessions,
        loadSession,
        deleteSession,
        createSession,
    } = useChatStore();

    // Check backend availability and load sessions
    const checkAndLoadSessions = useCallback(async () => {
        const isAvailable = await sessionAPI.checkBackendAvailability();
        setIsBackendReady(isAvailable);
        
        if (isAvailable || retryCount >= 5) {
            // Load sessions if backend is available or we've retried enough
            await loadSessions(mode);
        }
        
        return isAvailable;
    }, [mode, loadSessions, retryCount]);

    // Load sessions on mount and when mode changes
    useEffect(() => {
        checkAndLoadSessions();
    }, [mode, checkAndLoadSessions]);

    // Auto-retry when backend is not available
    useEffect(() => {
        if (isBackendReady || retryCount >= 5) return;

        const timer = setTimeout(() => {
            setRetryCount(prev => prev + 1);
            checkAndLoadSessions();
        }, 2000); // Retry every 2 seconds

        return () => clearTimeout(timer);
    }, [isBackendReady, retryCount, checkAndLoadSessions]);

    const handleCreateSession = async () => {
        try {
            setIsCreating(true);
            setError(null);
            await createSession(mode);
        } catch (err) {
            setError("Failed to create session");
            console.error(err);
        } finally {
            setIsCreating(false);
        }
    };

    const handleLoadSession = async (sessionId: string) => {
        try {
            setError(null);
            await loadSession(sessionId);
        } catch (err) {
            setError("Failed to load session");
            console.error(err);
        }
    };

    const handleDeleteSession = async (sessionId: string) => {
        if (window.confirm("确定要删除这个会话吗？此操作不可恢复。")) {
            try {
                setError(null);
                await deleteSession(sessionId);
            } catch (err) {
                setError("Failed to delete session");
                console.error(err);
            }
        }
    };

    const filteredSessions = sessions.filter(s => s.type === mode);

    const handleRetry = async () => {
        setRetryCount(0);
        setError(null);
        await checkAndLoadSessions();
    };

    return (
        <div className="space-y-3">
            {/* Header with New Conversation button */}
            <div className="flex items-center justify-between px-1">
                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    {mode === "rag" ? "问答历史" : "解题历史"}
                </h3>
                <button
                    onClick={handleCreateSession}
                    disabled={isCreating || !isBackendReady}
                    className="
                        flex items-center gap-1 px-2 py-1
                        text-xs font-medium text-blue-600
                        bg-blue-50 hover:bg-blue-100 disabled:opacity-50
                        rounded-md transition-colors
                    "
                    title="新建会话"
                >
                    {isCreating ? (
                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                        <Plus className="w-3.5 h-3.5" />
                    )}
                    新建
                </button>
            </div>

            {/* Backend unavailable warning */}
            {!isBackendReady && (
                <div className="flex items-center gap-2 p-2 bg-amber-50 rounded-lg text-amber-700 text-xs">
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    <span className="flex-1">后端服务未启动或不可用</span>
                    <button
                        onClick={handleRetry}
                        disabled={isLoadingSessions}
                        className="flex items-center gap-1 px-2 py-1 bg-amber-100 hover:bg-amber-200 rounded transition-colors"
                        title="重试连接"
                    >
                        {isLoadingSessions ? (
                            <Loader2 className="w-3 h-3 animate-spin" />
                        ) : (
                            <RefreshCw className="w-3 h-3" />
                        )}
                        重试
                    </button>
                </div>
            )}

            {/* Error message */}
            {error && (
                <div className="flex items-center gap-2 p-2 bg-red-50 rounded-lg text-red-600 text-xs">
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    <span>{error}</span>
                </div>
            )}

            {/* Session list */}
            <div className="space-y-1 max-h-[300px] overflow-y-auto pr-1 scrollbar-thin">
                {isLoadingSessions ? (
                    <div className="flex items-center justify-center py-8 text-gray-400">
                        <Loader2 className="w-5 h-5 animate-spin mr-2" />
                        <span className="text-sm">加载中...</span>
                    </div>
                ) : !isBackendReady ? (
                    <div className="text-center py-8 text-gray-400">
                        <p className="text-sm">无法加载会话</p>
                        <p className="text-xs mt-1">请检查后端服务状态</p>
                    </div>
                ) : filteredSessions.length === 0 ? (
                    <div className="text-center py-8 text-gray-400">
                        <p className="text-sm">暂无会话</p>
                        <p className="text-xs mt-1">点击"新建"开始</p>
                    </div>
                ) : (
                    filteredSessions.map((session) => (
                        <ConversationCard
                            key={session.id}
                            session={session}
                            isActive={session.id === currentSessionId}
                            onClick={() => handleLoadSession(session.id)}
                            onDelete={() => handleDeleteSession(session.id)}
                        />
                    ))
                )}
            </div>
        </div>
    );
}
