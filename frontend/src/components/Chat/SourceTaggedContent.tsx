/**
 * 来源标记内容组件
 * 
 * 解析并渲染带有来源标记的 Markdown 内容。
 * 支持将不同来源的内容分段展示，带有视觉区分。
 * 
 * 格式：
 * - [知识库检索] 内容...
 * - [网页检索] 内容... (来源: URL)
 * 
 * @example
 * ```tsx
 * <SourceTaggedContent content="[知识库检索] 动态规划是一种..." />
 * ```
 */

import { Database, Globe, ExternalLink } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { CodeBlock } from "./CodeBlock";

/** 来源段落接口 */
export interface SourceSegment {
    /** 来源类型 */
    source_type: "vector_db" | "web_search";
    /** 内容 */
    content: string;
    /** 来源URL */
    url?: string;
    /** 来源标题 */
    title?: string;
}

/** 来源标记内容属性 */
interface SourceTaggedContentProps {
    /** 带来源标记的原始内容 */
    content: string;
}

/**
 * 解析带有来源标记的内容
 * 
 * 从文本中提取来源标记，分割成多个段落。
 * 支持以下格式：
 * - [知识库检索] 内容...
 * - [网页检索] 内容... (来源: URL)
 * 
 * @param content - 带来源标记的原始内容
 * @returns 分段后的内容数组
 */
export function parseSourceSegments(content: string): SourceSegment[] {
    const segments: SourceSegment[] = [];

    // 匹配 [知识库检索] 或 [网页检索] 开头的段落
    const pattern = /(\[(?:知识库检索|网页检索)\])([\s\S]*?)(?=\[(?:知识库检索|网页检索)\]|$)/g;

    let match;
    while ((match = pattern.exec(content)) !== null) {
        const tag = match[1];
        const segmentContent = match[2].trim();

        // 确定来源类型
        const source_type = tag === "[知识库检索]" ? "vector_db" : "web_search";

        // 提取URL (来源: xxx)
        let url: string | undefined;
        let cleanContent = segmentContent;

        const sourceMatch = segmentContent.match(/\(来源:\s*(https?:\/\/[^\s)]+)\)/);
        if (sourceMatch) {
            url = sourceMatch[1];
            // 移除来源标注，保留纯内容
            cleanContent = segmentContent.replace(/\(来源:\s*https?:\/\/[^\s)]+\)/, "").trim();
        }

        segments.push({
            source_type,
            content: cleanContent,
            url,
        });
    }

    // 如果没有匹配到任何来源标记，将整个内容作为一个无来源段落
    if (segments.length === 0) {
        segments.push({
            source_type: "vector_db",
            content: content.trim(),
        });
    }

    return segments;
}

/**
 * 来源标记内容组件
 * 
 * 渲染带有来源标记的 Markdown 内容，每个来源段落有独立的样式。
 * 
 * @param content - 带来源标记的原始内容
 */
export function SourceTaggedContent({ content }: SourceTaggedContentProps) {
    const segments = parseSourceSegments(content);

    return (
        <div className="space-y-4">
            {segments.map((segment, index) => (
                <SourceSegmentBlock key={index} segment={segment} />
            ))}
        </div>
    );
}

/** 来源段落块属性 */
interface SourceSegmentBlockProps {
    segment: SourceSegment;
}

/**
 * 单个来源段落块
 * 
 * 渲染单个来源段落，包括来源标记和 Markdown 内容。
 * 根据来源类型显示不同的视觉样式。
 * 
 * @param segment - 来源段落数据
 */
function SourceSegmentBlock({ segment }: SourceSegmentBlockProps) {
    const isVectorDB = segment.source_type === "vector_db";

    return (
        <div
            className={`relative pl-4 border-l-2 ${
                isVectorDB
                    ? "border-blue-400 bg-blue-50/30"
                    : "border-purple-400 bg-purple-50/30"
            }`}
        >
            {/* 来源标记 */}
            <div
                className={`flex items-center gap-1.5 mb-2 text-xs font-medium ${
                    isVectorDB ? "text-blue-700" : "text-purple-700"
                }`}
            >
                {isVectorDB ? (
                    <>
                        <Database className="w-3.5 h-3.5" />
                        <span>知识库检索</span>
                    </>
                ) : (
                    <>
                        <Globe className="w-3.5 h-3.5" />
                        <span>网页检索</span>
                    </>
                )}

                {segment.url && (
                    <a
                        href={segment.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="ml-2 inline-flex items-center gap-0.5 text-purple-600 hover:text-purple-800 hover:underline"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <ExternalLink className="w-3 h-3" />
                        来源
                    </a>
                )}
            </div>

            {/* 内容渲染 */}
            <div className="text-gray-700">
                <ReactMarkdown
                    remarkPlugins={[[remarkGfm, { singleTilde: false }]]}
                    components={{
                        p({ children }) {
                            return (
                                <p className="text-gray-700 leading-relaxed mb-2">
                                    {children}
                                </p>
                            );
                        },
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
                            return <div className="my-2">{children}</div>;
                        },
                        ul({ children }) {
                            return (
                                <ul className="list-disc list-inside space-y-1 mb-2 text-gray-700">
                                    {children}
                                </ul>
                            );
                        },
                        ol({ children }) {
                            return (
                                <ol className="list-decimal list-inside space-y-1 mb-2 text-gray-700">
                                    {children}
                                </ol>
                            );
                        },
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
                    {segment.content}
                </ReactMarkdown>
            </div>
        </div>
    );
}
