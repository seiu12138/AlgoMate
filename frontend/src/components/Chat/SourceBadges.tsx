import { Database, Globe, ExternalLink } from "lucide-react";

export interface Source {
    type: "vector_db" | "web_search";
    url?: string;
    title?: string;
    score?: number;
    doc_id?: string;
}

interface SourceBadgeProps {
    source: Source;
}

export function SourceBadge({ source }: SourceBadgeProps) {
    if (source.type === "vector_db") {
        return (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium bg-blue-50 text-blue-700 rounded border border-blue-200">
                <Database className="w-3 h-3" />
                知识库
            </span>
        );
    }

    return (
        <a
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium bg-purple-50 text-purple-700 rounded border border-purple-200 hover:bg-purple-100 transition-colors"
            onClick={(e) => e.stopPropagation()}
        >
            <Globe className="w-3 h-3" />
            网页
            <ExternalLink className="w-3 h-3 ml-0.5" />
        </a>
    );
}

interface SourceListProps {
    sources: Source[];
    summary?: {
        vector_db_count: number;
        web_search_count: number;
        evaluation_score?: number;
        needs_web_search: boolean;
    };
}

export function SourceList({ sources, summary }: SourceListProps) {
    if (!sources || sources.length === 0) return null;

    const vectorSources = sources.filter((s) => s.type === "vector_db");
    const webSources = sources.filter((s) => s.type === "web_search");

    return (
        <div className="mb-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
            {/* 摘要信息 */}
            {summary && (
                <div className="flex items-center gap-3 mb-2 text-xs text-gray-500 pb-2 border-b border-gray-200">
                    {summary.vector_db_count > 0 && (
                        <span className="flex items-center gap-1">
                            <Database className="w-3 h-3" />
                            知识库: {summary.vector_db_count}
                        </span>
                    )}
                    {summary.web_search_count > 0 && (
                        <span className="flex items-center gap-1">
                            <Globe className="w-3 h-3" />
                            网页: {summary.web_search_count}
                        </span>
                    )}
                    {summary.evaluation_score !== undefined && (
                        <span className="ml-auto">
                            检索评分: {(summary.evaluation_score * 100).toFixed(0)}%
                        </span>
                    )}
                </div>
            )}

            {/* 来源徽章 */}
            <div className="flex flex-wrap gap-2">
                {vectorSources.length > 0 && (
                    <SourceBadge source={{ type: "vector_db" }} />
                )}
                {webSources.map((source, index) => (
                    <SourceBadge key={`web-${index}`} source={source} />
                ))}
            </div>

            {/* 网页来源详情 */}
            {webSources.length > 0 && (
                <div className="mt-2 space-y-1">
                    {webSources.map((source, index) =>
                        source.url ? (
                            <a
                                key={`web-detail-${index}`}
                                href={source.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="block text-xs text-purple-600 hover:text-purple-800 hover:underline truncate"
                                title={source.title || source.url}
                            >
                                {source.title || source.url}
                            </a>
                        ) : null
                    )}
                </div>
            )}
        </div>
    );
}
