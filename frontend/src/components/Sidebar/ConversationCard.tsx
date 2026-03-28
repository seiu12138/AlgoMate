import { Trash2, MessageSquare } from "lucide-react";
import type { ConversationSession } from "../../types";

interface ConversationCardProps {
    session: ConversationSession;
    isActive: boolean;
    onClick: () => void;
    onDelete: () => void;
}

export function ConversationCard({ session, isActive, onClick, onDelete }: ConversationCardProps) {
    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
        
        if (diffDays === 0) {
            return date.toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" });
        } else if (diffDays === 1) {
            return "昨天";
        } else if (diffDays < 7) {
            return date.toLocaleDateString("zh-CN", { weekday: "short" });
        } else {
            return date.toLocaleDateString("zh-CN", { month: "short", day: "numeric" });
        }
    };

    return (
        <div
            className={`
                group relative p-3 rounded-lg cursor-pointer transition-all duration-200
                ${isActive 
                    ? "bg-gradient-to-r from-blue-500/20 to-purple-500/20 border border-blue-300/50 shadow-sm" 
                    : "hover:bg-white/40 border border-transparent"
                }
            `}
            onClick={onClick}
        >
            <div className="flex items-start gap-2">
                <MessageSquare className={`
                    w-4 h-4 mt-0.5 flex-shrink-0
                    ${isActive ? "text-blue-600" : "text-gray-400"}
                `} />
                <div className="flex-1 min-w-0">
                    <h4 className={`
                        text-sm font-medium truncate
                        ${isActive ? "text-blue-900" : "text-gray-700"}
                    `}>
                        {session.title || "New Conversation"}
                    </h4>
                    <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs text-gray-400">
                            {formatDate(session.updatedAt)}
                        </span>
                        <span className="text-xs text-gray-300">•</span>
                        <span className="text-xs text-gray-400">
                            {session.messageCount} 消息
                        </span>
                    </div>
                    {session.lastMessagePreview && (
                        <p className="text-xs text-gray-400 truncate mt-1">
                            {session.lastMessagePreview}
                        </p>
                    )}
                </div>
            </div>
            
            {/* Delete button - shows on hover */}
            <button
                className="
                    absolute right-2 top-1/2 -translate-y-1/2
                    p-1.5 rounded-md
                    opacity-0 group-hover:opacity-100
                    hover:bg-red-100 hover:text-red-600
                    text-gray-400
                    transition-all duration-200
                "
                onClick={(e) => {
                    e.stopPropagation();
                    onDelete();
                }}
                title="删除会话"
            >
                <Trash2 className="w-3.5 h-3.5" />
            </button>
        </div>
    );
}
