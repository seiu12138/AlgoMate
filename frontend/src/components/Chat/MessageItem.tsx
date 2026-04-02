import { User, Bot, CheckCircle } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Message } from "../../types";
import { CodeBlock } from "./CodeBlock";
import { ExecutionResult } from "./ExecutionResult";
import { ExecutionHistory } from "./ExecutionHistory";
import { SourceTaggedContent, parseSourceSegments } from "./SourceTaggedContent";
import { SourceList } from "./SourceBadges";

interface MessageItemProps {
    message: Message;
}

export function MessageItem({ message }: MessageItemProps) {
    const isUser = message.role === "user";
    const { agentResult } = message;
    
    // Check if content has source tags
    const hasSourceTags = !isUser && (
        message.content.includes("[知识库检索]") || 
        message.content.includes("[网页检索]")
    );

    return (
        <div className={`flex gap-4 ${isUser ? "flex-row-reverse" : ""} animate-fade-in`}>
            {/* 头像 */}
            <div className={`flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center ${
                isUser 
                    ? "bg-gradient-to-br from-blue-500 to-blue-600 shadow-lg shadow-blue-500/20" 
                    : "bg-gradient-to-br from-purple-500 to-purple-600 shadow-lg shadow-purple-500/20"
            }`}>
                {isUser ? (
                    <User className="w-5 h-5 text-white" />
                ) : (
                    <Bot className="w-5 h-5 text-white" />
                )}
            </div>

            {/* 消息内容 */}
            <div className={`flex-1 max-w-[85%] ${isUser ? "message-user" : "message-ai"} p-4`}>
                {/* 来源标记内容 或 普通 Markdown */}
                <div className="markdown-body">
                    {hasSourceTags ? (
                        <SourceTaggedContent content={message.content} />
                    ) : (
                    <ReactMarkdown
                        remarkPlugins={[[remarkGfm, { singleTilde: false }]]}
                        components={{
                            // 标题渲染
                            h1({ children }) {
                                return (
                                    <h1 className="text-xl font-bold text-gray-900 mt-4 mb-3 pb-2 border-b border-gray-200">
                                        {children}
                                    </h1>
                                );
                            },
                            h2({ children }) {
                                return (
                                    <h2 className="text-lg font-bold text-gray-800 mt-4 mb-2">
                                        {children}
                                    </h2>
                                );
                            },
                            h3({ children }) {
                                return (
                                    <h3 className="text-base font-semibold text-gray-800 mt-3 mb-2">
                                        {children}
                                    </h3>
                                );
                            },
                            h4({ children }) {
                                return (
                                    <h4 className="text-sm font-semibold text-gray-700 mt-2 mb-1">
                                        {children}
                                    </h4>
                                );
                            },
                            // 段落
                            p({ children }) {
                                return (
                                    <p className="text-gray-700 leading-relaxed mb-3">
                                        {children}
                                    </p>
                                );
                            },
                            // 代码块
                            code({ node, inline, className, children, ...props }: any) {
                                const match = /language-(\w+)/.exec(className || "");
                                const code = String(children).replace(/\n$/, "");

                                if (!inline && match) {
                                    return <CodeBlock code={code} language={match[1]} />;
                                }

                                return (
                                    <code
                                        className="px-1.5 py-0.5 bg-gray-100 rounded text-sm font-mono text-gray-800"
                                        {...props}
                                    >
                                        {children}
                                    </code>
                                );
                            },
                            pre({ children }) {
                                return <div className="my-3">{children}</div>;
                            },
                            // 列表 - 普通列表
                            ul({ children, className }) {
                                // 任务列表会有 contains-task-list class
                                const isTaskList = className?.includes("contains-task-list");
                                return (
                                    <ul
                                        className={`${
                                            isTaskList
                                                ? "space-y-1 mb-3 text-gray-700 list-none pl-0"
                                                : "list-disc list-inside space-y-1 mb-3 text-gray-700"
                                        }`}
                                    >
                                        {children}
                                    </ul>
                                );
                            },
                            ol({ children }) {
                                return (
                                    <ol className="list-decimal list-inside space-y-1 mb-3 text-gray-700">
                                        {children}
                                    </ol>
                                );
                            },
                            // 列表项 - 处理任务列表
                            li({ children, className }) {
                                const isTaskListItem = className?.includes("task-list-item");
                                if (isTaskListItem) {
                                    return (
                                        <li className="flex items-start gap-2 mb-1">
                                            {children}
                                        </li>
                                    );
                                }
                                return <li className="ml-2">{children}</li>;
                            },
                            // 复选框 - 用于任务列表
                            input({ checked, type }) {
                                if (type === "checkbox") {
                                    return (
                                        <input
                                            type="checkbox"
                                            checked={checked}
                                            readOnly
                                            className="mt-1 w-4 h-4 text-purple-600 rounded border-gray-300 focus:ring-purple-500 cursor-default"
                                        />
                                    );
                                }
                                return <input type={type} />;
                            },
                            // 表格
                            table({ children }) {
                                return (
                                    <div className="overflow-x-auto my-4 rounded-lg border border-gray-200">
                                        <table className="w-full text-sm text-left text-gray-700">
                                            {children}
                                        </table>
                                    </div>
                                );
                            },
                            thead({ children }) {
                                return (
                                    <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                                        {children}
                                    </thead>
                                );
                            },
                            tbody({ children }) {
                                return <tbody className="divide-y divide-gray-200 bg-white">{children}</tbody>;
                            },
                            tr({ children }) {
                                return <tr className="hover:bg-gray-50">{children}</tr>;
                            },
                            th({ children }) {
                                return (
                                    <th className="px-4 py-3 font-semibold text-gray-900">
                                        {children}
                                    </th>
                                );
                            },
                            td({ children }) {
                                return <td className="px-4 py-3">{children}</td>;
                            },
                            // 删除线
                            del({ children }) {
                                return (
                                    <del className="line-through text-gray-500">
                                        {children}
                                    </del>
                                );
                            },
                            // 分隔线
                            hr() {
                                return <hr className="my-4 border-t border-gray-200" />;
                            },
                            // 引用
                            blockquote({ children }) {
                                return (
                                    <blockquote className="border-l-4 border-purple-300 pl-4 my-3 text-gray-600 italic bg-gray-50 py-2 pr-2 rounded-r">
                                        {children}
                                    </blockquote>
                                );
                            },
                            // 加粗和斜体
                            strong({ children }) {
                                return <strong className="font-bold text-gray-900">{children}</strong>;
                            },
                            em({ children }) {
                                return <em className="italic">{children}</em>;
                            },
                            // 链接
                            a({ children, href }) {
                                return (
                                    <a
                                        href={href}
                                        className="text-purple-600 hover:text-purple-800 underline"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                    >
                                        {children}
                                    </a>
                                );
                            },
                        }}
                    >
                        {message.content}
                    </ReactMarkdown>
                    )}
                </div>

                {/* Agent 结果 */}
                {agentResult && (
                    <div className="mt-4 space-y-3">
                        {/* 生成的代码 */}
                        {agentResult.generatedCode && (
                            <div>
                                <div className="flex items-center gap-2 mb-2">
                                    <span className="text-xs font-medium text-purple-600 bg-purple-50 px-2 py-1 rounded">
                                        生成代码
                                    </span>
                                    {agentResult.isSolved && (
                                        <span className="flex items-center gap-1 text-xs text-green-600 bg-green-50 px-2 py-1 rounded">
                                            <CheckCircle className="w-3 h-3" />
                                            已解决
                                        </span>
                                    )}
                                </div>
                                <CodeBlock code={agentResult.generatedCode} language="python" />
                            </div>
                        )}

                        {/* 执行结果 */}
                        {agentResult.executionResult && (
                            <ExecutionResult result={agentResult.executionResult} />
                        )}

                        {/* 执行历史 */}
                        {agentResult.executionHistory && agentResult.executionHistory.length > 0 && (
                            <ExecutionHistory history={agentResult.executionHistory} />
                        )}
                    </div>
                )}

                {/* 时间戳 */}
                <div className="mt-2 text-xs text-gray-400">
                    {new Date(message.timestamp).toLocaleTimeString()}
                </div>
            </div>
        </div>
    );
}
