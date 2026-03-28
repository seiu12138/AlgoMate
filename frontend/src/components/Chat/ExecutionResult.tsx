import { CheckCircle, XCircle, Clock, Terminal } from "lucide-react";
import type { ExecutionResult as ExecutionResultType } from "../../types";

interface ExecutionResultProps {
    result: ExecutionResultType;
}

export function ExecutionResult({ result }: ExecutionResultProps) {
    const { success, stdout, stderr, exitCode, executionTime, errorType } = result;

    return (
        <div className="execution-panel mt-4 overflow-hidden">
            {/* 头部 */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700/50">
                <div className="flex items-center gap-2">
                    <Terminal className="w-4 h-4 text-slate-400" />
                    <span className="text-sm font-medium text-slate-200">执行结果</span>
                </div>
                <div className={`flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-medium ${
                    success 
                        ? "bg-green-500/20 text-green-400" 
                        : "bg-red-500/20 text-red-400"
                }`}>
                    {success ? (
                        <>
                            <CheckCircle className="w-3.5 h-3.5" />
                            成功
                        </>
                    ) : (
                        <>
                            <XCircle className="w-3.5 h-3.5" />
                            失败
                        </>
                    )}
                </div>
            </div>

            {/* 执行信息 */}
            <div className="flex items-center gap-6 px-4 py-2 bg-slate-800/30 text-xs text-slate-400 border-b border-slate-700/50">
                <div className="flex items-center gap-1.5">
                    <span>Exit Code:</span>
                    <span className={success ? "text-green-400" : "text-red-400"}>{exitCode}</span>
                </div>
                <div className="flex items-center gap-1.5">
                    <Clock className="w-3 h-3" />
                    <span>{executionTime.toFixed(3)}s</span>
                </div>
                {errorType && (
                    <div className="flex items-center gap-1.5">
                        <span>Error:</span>
                        <span className="text-red-400">{errorType}</span>
                    </div>
                )}
            </div>

            {/* 输出内容 */}
            <div className="p-4 space-y-3">
                {stdout && (
                    <div>
                        <div className="text-xs text-slate-500 mb-1.5">标准输出</div>
                        <pre className="bg-slate-950/50 rounded-lg p-3 text-sm text-slate-300 font-mono whitespace-pre-wrap">
                            {stdout}
                        </pre>
                    </div>
                )}
                {stderr && (
                    <div>
                        <div className="text-xs text-red-400/70 mb-1.5">标准错误</div>
                        <pre className="bg-red-950/20 rounded-lg p-3 text-sm text-red-300 font-mono whitespace-pre-wrap">
                            {stderr}
                        </pre>
                    </div>
                )}
            </div>
        </div>
    );
}
