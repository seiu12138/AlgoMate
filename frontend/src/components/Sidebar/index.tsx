import { GraduationCap } from "lucide-react";
import { ModeSelector } from "./ModeSelector";
import { AgentConfig } from "./AgentConfig";
import { ActionButtons } from "./ActionButtons";
import { useChatStore } from "../../stores/chatStore";
import { useConfigStore } from "../../stores/configStore";

export function Sidebar() {
    const { messages, mode, setMode, clearMessages } = useChatStore();
    const { language, maxIterations, setLanguage, setMaxIterations } = useConfigStore();

    return (
        <aside className="fixed left-0 top-0 h-full w-[260px] sidebar-gradient backdrop-blur-xl border-r border-white/40 flex flex-col z-10">
            {/* 标题区域 */}
            <div className="p-5 border-b border-white/30">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
                        <GraduationCap className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h1 className="text-lg font-bold gradient-title">AlgoMate</h1>
                        <p className="text-xs text-gray-500">智能算法辅导系统</p>
                    </div>
                </div>
            </div>

            {/* 配置区域 */}
            <div className="flex-1 p-4 space-y-4 overflow-y-auto">
                {/* 模式选择 */}
                <ModeSelector mode={mode} onModeChange={setMode} />

                {/* Agent 配置 - 仅在 Agent 模式下显示 */}
                {mode === "agent" && (
                    <AgentConfig
                        language={language}
                        maxIterations={maxIterations}
                        onLanguageChange={setLanguage}
                        onMaxIterationsChange={setMaxIterations}
                    />
                )}
            </div>

            {/* 底部操作区 */}
            <div className="p-4 border-t border-white/30">
                <ActionButtons 
                    onClearMessages={clearMessages}
                    disabled={messages.length === 0}
                />
            </div>
        </aside>
    );
}
