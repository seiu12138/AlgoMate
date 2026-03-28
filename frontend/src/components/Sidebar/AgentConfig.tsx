import { Code2, RotateCcw } from "lucide-react";
import type { Language } from "../../types";

interface AgentConfigProps {
    language: Language;
    maxIterations: number;
    onLanguageChange: (language: Language) => void;
    onMaxIterationsChange: (iterations: number) => void;
}

const languages: { value: Language; label: string }[] = [
    { value: "python", label: "Python" },
    { value: "cpp", label: "C++" },
    { value: "java", label: "Java" },
];

export function AgentConfig({
    language,
    maxIterations,
    onLanguageChange,
    onMaxIterationsChange,
}: AgentConfigProps) {
    return (
        <div className="space-y-4 p-4 bg-white/40 rounded-xl border border-white/50">
            <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
                <Code2 className="w-4 h-4 text-purple-500" />
                Agent 配置
            </div>
            
            {/* 语言选择 */}
            <div className="space-y-2">
                <label className="text-xs text-gray-500">编程语言</label>
                <select
                    value={language}
                    onChange={(e) => onLanguageChange(e.target.value as Language)}
                    className="w-full px-3 py-2 bg-white/70 border border-white/60 rounded-lg text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-purple-500/30 focus:border-purple-500/50"
                >
                    {languages.map((lang) => (
                        <option key={lang.value} value={lang.value}>
                            {lang.label}
                        </option>
                    ))}
                </select>
            </div>

            {/* 迭代次数 */}
            <div className="space-y-2">
                <label className="text-xs text-gray-500 flex items-center justify-between">
                    <span>最大迭代次数</span>
                    <span className="text-purple-600 font-medium">{maxIterations}</span>
                </label>
                <div className="flex items-center gap-2">
                    <input
                        type="range"
                        min={1}
                        max={10}
                        value={maxIterations}
                        onChange={(e) => onMaxIterationsChange(Number(e.target.value))}
                        className="flex-1 h-2 bg-white/60 rounded-lg appearance-none cursor-pointer accent-purple-500"
                    />
                    <RotateCcw className="w-4 h-4 text-gray-400" />
                </div>
            </div>
        </div>
    );
}
