import { useState } from "react";
import { History, ChevronDown, ChevronRight, Code2, Play } from "lucide-react";
import type { ExecutionHistoryItem } from "../../types";
import { CodeBlock } from "./CodeBlock";
import { ExecutionResult } from "./ExecutionResult";

interface ExecutionHistoryProps {
    history: ExecutionHistoryItem[];
}

export function ExecutionHistory({ history }: ExecutionHistoryProps) {
    const [expandedIterations, setExpandedIterations] = useState<Set<number>>(new Set());

    const toggleIteration = (iteration: number) => {
        const newSet = new Set(expandedIterations);
        if (newSet.has(iteration)) {
            newSet.delete(iteration);
        } else {
            newSet.add(iteration);
        }
        setExpandedIterations(newSet);
    };

    if (!history || history.length === 0) return null;

    return (
        <div className="mt-4 border border-slate-200/50 rounded-xl overflow-hidden bg-white/40 backdrop-blur-sm">
            {/* 头部 */}
            <div className="flex items-center justify-between px-4 py-3 bg-slate-50/50 border-b border-slate-200/50">
                <div className="flex items-center gap-2">
                    <History className="w-4 h-4 text-purple-500" />
                    <span className="text-sm font-medium text-gray-700">执行历史</span>
                    <span className="px-2 py-0.5 bg-purple-100 text-purple-600 rounded-full text-xs">
                        {history.length} 次迭代
                    </span>
                </div>
            </div>

            {/* 历史列表 */}
            <div className="divide-y divide-slate-200/50">
                {history.map((item) => {
                    const isExpanded = expandedIterations.has(item.iteration);
                    const hasError = !item.result.success;

                    return (
                        <div key={item.iteration} className="bg-white/30">
                            {/* 迭代头部 */}
                            <button
                                onClick={() => toggleIteration(item.iteration)}
                                className="w-full flex items-center justify-between px-4 py-3 hover:bg-white/50 transition-colors"
                            >
                                <div className="flex items-center gap-3">
                                    <span className="flex items-center justify-center w-6 h-6 rounded-full bg-purple-100 text-purple-600 text-xs font-medium">
                                        {item.iteration}
                                    </span>
                                    <div className="flex items-center gap-2 text-sm text-gray-600">
                                        <Code2 className="w-3.5 h-3.5" />
                                        <span>代码</span>
                                        {hasError && (
                                            <span className="px-1.5 py-0.5 bg-red-100 text-red-600 rounded text-xs">
                                                错误
                                            </span>
                                        )}
                                    </div>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Play className="w-3.5 h-3.5 text-gray-400" />
                                    {isExpanded ? (
                                        <ChevronDown className="w-4 h-4 text-gray-400" />
                                    ) : (
                                        <ChevronRight className="w-4 h-4 text-gray-400" />
                                    )}
                                </div>
                            </button>

                            {/* 展开内容 */}
                            {isExpanded && (
                                <div className="px-4 pb-4 space-y-4 animate-fade-in">
                                    <CodeBlock code={item.code} language="python" />
                                    <ExecutionResult result={item.result} />
                                    {item.fixes && (
                                        <div className="p-3 bg-blue-50/50 rounded-lg border border-blue-200/50">
                                            <div className="text-xs text-blue-600 mb-1.5">修复建议</div>
                                            <p className="text-sm text-blue-800">{item.fixes}</p>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
