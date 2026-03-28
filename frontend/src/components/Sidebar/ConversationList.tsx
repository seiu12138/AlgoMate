import { useEffect } from "react";
import { Plus, Loader2 } from "lucide-react";
import { ConversationCard } from "./ConversationCard";
import { useChatStore } from "../../stores/chatStore";
import type { Mode } from "../../types";

interface ConversationListProps {
    mode: Mode;
}

export function ConversationList({ mode }: ConversationListProps) {
    const {
        sessions,
        currentSessionId,
        isLoadingSessions,
        loadSessions,
        loadSession,
        deleteSession,
        createSession,
    } = useChatStore();

    // Load sessions on mount and when mode changes
    useEffect(() => {
        loadSessions(mode);
    }, [mode, loadSessions]);

    const handleCreateSession = async () => {
        await createSession(mode);
    };

    const handleLoadSession = async (sessionId: string) => {
        await loadSession(sessionId);
    };

    const handleDeleteSession = async (sessionId: string) => {
        if (window.confirm("确定要删除这个会话吗？此操作不可恢复。")) {
            await deleteSession(sessionId);
        }
    };

    const filteredSessions = sessions.filter(s => s.type === mode);

    return (
        <div className="space-y-3">
            {/* Header with New Conversation button */}
            <div className="flex items-center justify-between px-1">
                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    {mode === "rag" ? "问答历史" : "解题历史"}
                </h3>
                <button
                    onClick={handleCreateSession}
                    className="
                        flex items-center gap-1 px-2 py-1
                        text-xs font-medium text-blue-600
                        bg-blue-50 hover:bg-blue-100
                        rounded-md transition-colors
                    "
                    title="新建会话"
                >
                    <Plus className="w-3.5 h-3.5" />
                    新建
                </button>
            </div>

            {/* Session list */}
            <div className="space-y-1 max-h-[300px] overflow-y-auto pr-1 scrollbar-thin">
                {isLoadingSessions ? (
                    <div className="flex items-center justify-center py-8 text-gray-400">
                        <Loader2 className="w-5 h-5 animate-spin mr-2" />
                        <span className="text-sm">加载中...</span>
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
