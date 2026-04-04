/**
 * 来源徽章组件 - 编号引用格式 [1][2]
 * 
 * 显示 RAG 检索结果的来源信息，以编号列表形式展示。
 * 支持点击跳转到网页来源。
 * 
 * @example
 * ```tsx
 * <SourceList sources={[
 *   { index: 1, type: "vector_db", title: "动态规划详解", preview: "..." },
 *   { index: 2, type: "web_search", title: "线段树优化", url: "...", preview: "..." }
 * ]} />
 * ```
 */

import { Database, Globe, ExternalLink, BookOpen } from "lucide-react";

/** 来源信息接口 - 编号引用格式 */
export interface Source {
    /** 编号 [1], [2]... */
    index: number;
    /** 来源类型：知识库或网页搜索 */
    type: "vector_db" | "web_search";
    /** 来源标题 */
    title: string;
    /** 来源URL（网页搜索时有） */
    url?: string;
    /** 内容预览 */
    preview?: string;
    /** 文档ID（知识库检索时有） */
    doc_id?: string;
}

/** 单个来源引用属性 */
interface SourceCitationProps {
    source: Source;
}

/**
 * 单个来源引用项
 * 
 * 显示编号、标题和来源类型
 */
function SourceCitationItem({ source }: SourceCitationProps) {
    const isWeb = source.type === "web_search";
    
    return (
        <div className="flex items-start gap-2 py-1.5 border-b border-gray-100 last:border-0">
            {/* 编号 */}
            <span className="flex-shrink-0 w-6 h-6 flex items-center justify-center text-xs font-medium bg-gray-100 text-gray-600 rounded">
                {source.index}
            </span>
            
            {/* 内容 */}
            <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1.5">
                    {isWeb ? (
                        <Globe className="w-3 h-3 text-purple-500" />
                    ) : (
                        <Database className="w-3 h-3 text-blue-500" />
                    )}
                    
                    {isWeb && source.url ? (
                        <a
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs font-medium text-purple-700 hover:text-purple-900 hover:underline truncate flex items-center gap-0.5"
                            onClick={(e) => e.stopPropagation()}
                        >
                            {source.title}
                            <ExternalLink className="w-2.5 h-2.5 flex-shrink-0" />
                        </a>
                    ) : (
                        <span className="text-xs font-medium text-blue-700 truncate">
                            {source.title}
                        </span>
                    )}
                </div>
                
                {/* 内容预览 */}
                {source.preview && (
                    <p className="text-xs text-gray-500 mt-0.5 line-clamp-1" title={source.preview}>
                        {source.preview}
                    </p>
                )}
            </div>
        </div>
    );
}

/** 来源列表属性 */
interface SourceListProps {
    /** 来源列表 */
    sources: Source[];
    /** 检索摘要统计 */
    summary?: {
        total_count: number;
        vector_db_count: number;
        web_search_count: number;
    };
}

/**
 * 来源列表组件 - 编号引用格式
 * 
 * 显示编号参考资料列表，按编号顺序展示。
 * 
 * @param sources - 来源列表
 * @param summary - 可选的检索统计摘要
 */
export function SourceList({ sources, summary }: SourceListProps) {
    if (!sources || sources.length === 0) return null;

    return (
        <div className="mb-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
            {/* 标题和摘要 */}
            <div className="flex items-center gap-2 mb-2 pb-2 border-b border-gray-200">
                <BookOpen className="w-4 h-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">
                    共参考 {summary?.total_count || sources.length} 篇资料
                </span>
                <span className="text-xs text-gray-400 ml-auto">
                    引用角标 [1] [2]... 可点击查看详情
                </span>
            </div>

            {/* 来源列表 */}
            <div className="space-y-0.5 max-h-48 overflow-y-auto">
                {sources.map((source) => (
                    <SourceCitationItem key={source.index} source={source} />
                ))}
            </div>
        </div>
    );
}

/**
 * 单个引用角标
 * 
 * 用于在消息内容中显示可点击的引用角标 [1] [2]...
 */
interface CitationBadgeProps {
    index: number;
    onClick?: () => void;
}

export function CitationBadge({ index, onClick }: CitationBadgeProps) {
    return (
        <sup
            className="inline-flex items-center justify-center w-4 h-4 text-[10px] font-medium bg-blue-100 text-blue-600 rounded cursor-pointer hover:bg-blue-200 transition-colors mx-0.5"
            onClick={onClick}
        >
            {index}
        </sup>
    );
}
