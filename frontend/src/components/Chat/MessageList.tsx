import { useEffect, useRef, useState } from "react";
import { useChatStore } from "../../stores/chatStore";
import { MessageItem } from "./MessageItem";
import { ProgressBar } from "../common/ProgressBar";
import { StatusBadge } from "../common/StatusBadge";
import { ChevronDown } from "lucide-react";
import { AlgoMateLogo } from "../Logo/AlgoMateLogo";

export function MessageList() {
    const { messages, isLoading, agentProgress, agentStatus } = useChatStore();
    const bottomRef = useRef<HTMLDivElement>(null);
    const [showScrollButton, setShowScrollButton] = useState(false);
    const [isUserScrolling, setIsUserScrolling] = useState(false);
    const lastMessageCountRef = useRef(messages.length);
    const scrollTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    // 获取消息容器（父元素的滚动容器）
    const getScrollContainer = () => {
        return bottomRef.current?.closest('.overflow-y-auto') as HTMLElement | null;
    };

    // 检查是否在底部附近
    const isNearBottom = () => {
        const container = getScrollContainer();
        if (!container) return true;
        const threshold = 100;
        return container.scrollHeight - container.scrollTop - container.clientHeight < threshold;
    };

    // 滚动到底部
    const scrollToBottom = (behavior: ScrollBehavior = "smooth") => {
        bottomRef.current?.scrollIntoView({ behavior });
    };

    // 监听滚动事件
    useEffect(() => {
        const container = getScrollContainer();
        if (!container) return;

        const handleScroll = () => {
            if (scrollTimeoutRef.current) {
                clearTimeout(scrollTimeoutRef.current);
            }
            
            setIsUserScrolling(true);
            
            const nearBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 100;
            setShowScrollButton(!nearBottom);
            
            scrollTimeoutRef.current = setTimeout(() => {
                setIsUserScrolling(false);
            }, 500);
        };

        container.addEventListener("scroll", handleScroll);
        return () => {
            container.removeEventListener("scroll", handleScroll);
            if (scrollTimeoutRef.current) {
                clearTimeout(scrollTimeoutRef.current);
            }
        };
    }, []);

    // 智能自动滚动
    useEffect(() => {
        // 如果用户正在手动滚动，不强制滚动
        if (isUserScrolling) return;

        const hasNewMessage = messages.length > lastMessageCountRef.current;
        lastMessageCountRef.current = messages.length;

        if (hasNewMessage) {
            // 用户发送新消息时滚动到底部
            scrollToBottom("smooth");
        } else if (isLoading && isNearBottom()) {
            // AI 回复中，如果在底部附近则跟随
            scrollToBottom("auto");
        }
    }, [messages, isLoading, agentProgress, agentStatus, isUserScrolling]);

    // 初始滚动
    useEffect(() => {
        if (messages.length > 0) {
            scrollToBottom("auto");
        }
    }, []);

    if (messages.length === 0) {
        return (
            <div className="h-full flex flex-col items-center justify-center text-center p-8">
                <div className="mb-6">
                    <AlgoMateLogo size={80} />
                </div>
                <h2 className="text-2xl font-bold gradient-title mb-3">
                    欢迎使用 AlgoMate
                </h2>
                <p className="text-gray-500 max-w-md mb-6">
                    我是您的智能算法辅导助手。您可以向我询问算法问题，或者使用 Agent 模式来解决编程题目。
                </p>
                <div className="flex gap-3">
                    <div className="px-4 py-2 bg-blue-50/80 rounded-lg text-sm text-blue-700 border border-blue-100">
                        🔍 RAG 模式 - 知识问答
                    </div>
                    <div className="px-4 py-2 bg-purple-50/80 rounded-lg text-sm text-purple-700 border border-purple-100">
                        🤖 Agent 模式 - 代码解题
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6 relative">
            {messages.map((message) => (
                <MessageItem key={message.id} message={message} />
            ))}

            {/* 加载状态 */}
            {isLoading && (
                <div className="flex items-center gap-3 p-4 message-ai">
                    <div className="flex-shrink-0 w-9 h-9 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center">
                        <span className="animate-pulse">🤖</span>
                    </div>
                    <div className="flex-1 space-y-2">
                        {agentStatus && (
                            <div className="flex items-center gap-2">
                                <StatusBadge status="pending" text={agentStatus} />
                            </div>
                        )}
                        {agentProgress > 0 && (
                            <ProgressBar progress={agentProgress} />
                        )}
                        {!agentStatus && agentProgress === 0 && (
                            <div className="flex items-center gap-2 text-gray-500">
                                <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                <span className="text-sm">思考中...</span>
                            </div>
                        )}
                    </div>
                </div>
            )}

            <div ref={bottomRef} />

            {/* 滚动到底部按钮 */}
            {showScrollButton && (
                <button
                    onClick={() => scrollToBottom("smooth")}
                    className="fixed bottom-24 left-1/2 -translate-x-1/2 z-10 flex items-center gap-1 px-3 py-2 bg-purple-600 text-white rounded-full shadow-lg hover:bg-purple-700 transition-colors"
                >
                    <ChevronDown className="w-4 h-4" />
                    <span className="text-sm">最新内容</span>
                </button>
            )}
        </div>
    );
}
