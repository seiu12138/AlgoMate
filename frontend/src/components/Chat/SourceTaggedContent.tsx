/**
 * 来源标记内容组件 - 编号引用格式 [1][2]
 * 
 * 渲染带有编号引用角标的 Markdown 内容。
 * 将 [1], [2] 等角标渲染为可点击的上标。
 * 
 * @example
 * ```tsx
 * <SourceTaggedContent 
 *   content="动态规划[1]是一种分治方法。根据线段树优化[2]的原理..."
 *   sources={[...]}
 * />
 * ```
 */

import { useState, useCallback, ReactNode } from "react";
import { Database, Globe, ExternalLink, X } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { CodeBlock } from "./CodeBlock";
import type { Source } from "./SourceBadges";

/** 来源标记内容属性 */
interface SourceTaggedContentProps {
    /** 带来源标记的原始内容 */
    content: string;
    /** 来源列表 */
    sources?: Source[];
}

/**
 * 递归处理 React children，将 [数字] 转换为引用角标组件
 */
function processChildrenForCitations(
    children: ReactNode,
    sources: Source[],
    onCitationClick: (index: number) => void
): ReactNode {
    // 如果是字符串，直接处理
    if (typeof children === "string") {
        return parseTextWithCitations(children, sources, onCitationClick);
    }

    // 如果是数组，递归处理每个元素
    if (Array.isArray(children)) {
        return children.map((child, i) => (
            <span key={i}>
                {processChildrenForCitations(child, sources, onCitationClick)}
            </span>
        ));
    }

    // 如果是 React 元素，递归处理其子元素
    if (children && typeof children === "object" && "props" in children) {
        const child = children as { props: { children?: ReactNode }; type: unknown };
        if (child.props && "children" in child.props) {
            return {
                ...child,
                props: {
                    ...child.props,
                    children: processChildrenForCitations(
                        child.props.children,
                        sources,
                        onCitationClick
                    ),
                },
            };
        }
    }

    // 其他情况直接返回
    return children;
}

/**
 * 解析文本中的引用角标 [1][2]...
 * 返回 React 元素数组
 */
function parseTextWithCitations(
    text: string,
    sources: Source[],
    onCitationClick: (index: number) => void
): ReactNode[] {
    const tokens: ReactNode[] = [];
    const regex = /\[(\d+)\]/g;
    let lastIndex = 0;
    let match;

    while ((match = regex.exec(text)) !== null) {
        // 添加角标前的文本
        if (match.index > lastIndex) {
            tokens.push(<span key={`text-${lastIndex}`}>{text.slice(lastIndex, match.index)}</span>);
        }

        // 添加引用角标
        const index = parseInt(match[1], 10);
        const hasSource = sources.some(s => s.index === index);
        
        tokens.push(
            <sup
                key={`cite-${index}`}
                className={`inline-flex items-center justify-center w-4 h-4 text-[10px] font-medium rounded cursor-pointer hover:bg-blue-200 transition-colors mx-0.5 align-super ${
                    hasSource 
                        ? "bg-blue-100 text-blue-600" 
                        : "bg-gray-100 text-gray-400"
                }`}
                onClick={() => hasSource && onCitationClick(index)}
                title={hasSource ? `查看引用 [${index}]` : `引用 [${index}]`}
            >
                {index}
            </sup>
        );

        lastIndex = regex.lastIndex;
    }

    // 添加剩余的文本
    if (lastIndex < text.length) {
        tokens.push(<span key={`text-end`}>{text.slice(lastIndex)}</span>);
    }

    return tokens.length > 0 ? tokens : [text];
}

/**
 * 来源标记内容组件
 * 
 * 渲染 Markdown 内容，并将 [1][2] 等角标渲染为可点击的上标。
 * 
 * @param content - 带来源标记的原始内容
 * @param sources - 可选的来源列表，用于显示引用详情
 */
export function SourceTaggedContent({ content, sources = [] }: SourceTaggedContentProps) {
    const [selectedSource, setSelectedSource] = useState<Source | null>(null);

    // 处理引用角标点击
    const handleCitationClick = useCallback((index: number) => {
        const source = sources.find((s) => s.index === index);
        if (source) {
            setSelectedSource(source);
        }
    }, [sources]);

    return (
        <div className="relative">
            {/* Markdown 内容 */}
            <div className="text-gray-700">
                <ReactMarkdown
                    remarkPlugins={[[remarkGfm, { singleTilde: false }]]}
                    components={{
                        // 文本节点 - 处理所有文本中的角标
                        text({ value }) {
                            return <>{parseTextWithCitations(value, sources, handleCitationClick)}</>;
                        },
                        // 标题
                        h1({ children }) {
                            return (
                                <h1 className="text-xl font-bold text-gray-900 mt-4 mb-3 pb-2 border-b border-gray-200">
                                    {processChildrenForCitations(children, sources, handleCitationClick)}
                                </h1>
                            );
                        },
                        h2({ children }) {
                            return (
                                <h2 className="text-lg font-bold text-gray-800 mt-4 mb-2">
                                    {processChildrenForCitations(children, sources, handleCitationClick)}
                                </h2>
                            );
                        },
                        h3({ children }) {
                            return (
                                <h3 className="text-base font-semibold text-gray-800 mt-3 mb-2">
                                    {processChildrenForCitations(children, sources, handleCitationClick)}
                                </h3>
                            );
                        },
                        h4({ children }) {
                            return (
                                <h4 className="text-sm font-semibold text-gray-700 mt-2 mb-1">
                                    {processChildrenForCitations(children, sources, handleCitationClick)}
                                </h4>
                            );
                        },
                        // 段落
                        p({ children }) {
                            return (
                                <p className="text-gray-700 leading-relaxed mb-3">
                                    {processChildrenForCitations(children, sources, handleCitationClick)}
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
                        // 列表
                        ul({ children, className }) {
                            const isTaskList = className?.includes("contains-task-list");
                            return (
                                <ul className={`${isTaskList ? "space-y-1 mb-3 text-gray-700 list-none pl-0" : "list-disc list-inside space-y-1 mb-3 text-gray-700"}`}>
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
                        li({ children, className }) {
                            const isTaskListItem = className?.includes("task-list-item");
                            if (isTaskListItem) {
                                return (
                                    <li className="flex items-start gap-2 mb-1">
                                        {processChildrenForCitations(children, sources, handleCitationClick)}
                                    </li>
                                );
                            }
                            return (
                                <li className="ml-2">
                                    {processChildrenForCitations(children, sources, handleCitationClick)}
                                </li>
                            );
                        },
                        // 强调
                        strong({ children }) {
                            return (
                                <strong className="font-bold text-gray-900">
                                    {processChildrenForCitations(children, sources, handleCitationClick)}
                                </strong>
                            );
                        },
                        em({ children }) {
                            return (
                                <em className="italic">
                                    {processChildrenForCitations(children, sources, handleCitationClick)}
                                </em>
                            );
                        },
                        del({ children }) {
                            return (
                                <del className="line-through text-gray-500">
                                    {processChildrenForCitations(children, sources, handleCitationClick)}
                                </del>
                            );
                        },
                        // 分隔线
                        hr() {
                            return <hr className="my-4 border-t border-gray-200" />;
                        },
                        // 引用块
                        blockquote({ children }) {
                            return (
                                <blockquote className="border-l-4 border-purple-300 pl-4 my-3 text-gray-600 italic bg-gray-50 py-2 pr-2 rounded-r">
                                    {processChildrenForCitations(children, sources, handleCitationClick)}
                                </blockquote>
                            );
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
                                    {processChildrenForCitations(children, sources, handleCitationClick)}
                                </a>
                            );
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
                                    {processChildrenForCitations(children, sources, handleCitationClick)}
                                </th>
                            );
                        },
                        td({ children }) {
                            return (
                                <td className="px-4 py-3">
                                    {processChildrenForCitations(children, sources, handleCitationClick)}
                                </td>
                            );
                        },
                    }}
                >
                    {content}
                </ReactMarkdown>
            </div>

            {/* 引用详情弹窗 */}
            {selectedSource && (
                <div className="absolute z-10 mt-2 p-3 bg-white rounded-lg shadow-lg border border-gray-200 max-w-sm">
                    <div className="flex items-start gap-2">
                        <span className="flex-shrink-0 w-6 h-6 flex items-center justify-center text-xs font-medium bg-blue-100 text-blue-600 rounded">
                            {selectedSource.index}
                        </span>
                        <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-1.5">
                                {selectedSource.type === "web_search" ? (
                                    <Globe className="w-3 h-3 text-purple-500" />
                                ) : (
                                    <Database className="w-3 h-3 text-blue-500" />
                                )}
                                <span className="text-sm font-medium text-gray-800 truncate">
                                    {selectedSource.title}
                                </span>
                            </div>
                            {selectedSource.preview && (
                                <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                                    {selectedSource.preview}
                                </p>
                            )}
                            {selectedSource.url && (
                                <a
                                    href={selectedSource.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="inline-flex items-center gap-1 mt-2 text-xs text-purple-600 hover:text-purple-800"
                                >
                                    <ExternalLink className="w-3 h-3" />
                                    访问来源
                                </a>
                            )}
                        </div>
                        <button
                            onClick={() => setSelectedSource(null)}
                            className="flex-shrink-0 p-1 text-gray-400 hover:text-gray-600"
                        >
                            <X className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}

/** 兼容旧接口 - 解析来源段落（已弃用） */
export interface SourceSegment {
    source_type: "vector_db" | "web_search";
    content: string;
    url?: string;
    title?: string;
}

/** 兼容旧接口（已弃用） */
export function parseSourceSegments(content: string): SourceSegment[] {
    // 新版不再按来源分割段落，直接返回整个内容
    return [{
        source_type: "vector_db",
        content: content,
    }];
}
