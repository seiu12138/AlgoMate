import { MessageSquare, Bot } from "lucide-react";
import type { Mode } from "../../types";

interface ModeSelectorProps {
    mode: Mode;
    onModeChange: (mode: Mode) => void;
}

export function ModeSelector({ mode, onModeChange }: ModeSelectorProps) {
    return (
        <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">模式选择</label>
            <div className="grid grid-cols-2 gap-2 p-1 bg-white/50 rounded-xl">
                <button
                    onClick={() => onModeChange("rag")}
                    className={`flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                        mode === "rag"
                            ? "bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-md"
                            : "text-gray-600 hover:bg-white/60"
                    }`}
                >
                    <MessageSquare className="w-4 h-4" />
                    RAG
                </button>
                <button
                    onClick={() => onModeChange("agent")}
                    className={`flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                        mode === "agent"
                            ? "bg-gradient-to-r from-purple-500 to-purple-600 text-white shadow-md"
                            : "text-gray-600 hover:bg-white/60"
                    }`}
                >
                    <Bot className="w-4 h-4" />
                    Agent
                </button>
            </div>
        </div>
    );
}
