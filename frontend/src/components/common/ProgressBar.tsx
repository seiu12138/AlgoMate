/**
 * 进度条组件
 * 
 * 显示一个带有动画效果的进度条，支持自定义进度值和标签显示。
 * 用于展示 Agent 解题流程的进度状态。
 * 
 * @example
 * ```tsx
 * <ProgressBar progress={75} showLabel={true} />
 * ```
 */

interface ProgressBarProps {
    /** 进度值 (0-100) */
    progress: number;
    /** 是否显示百分比标签，默认为 true */
    showLabel?: boolean;
}

/**
 * 进度条组件
 * 
 * @param progress - 当前进度值，会自动限制在 0-100 范围内
 * @param showLabel - 是否显示百分比标签
 */
export function ProgressBar({ progress, showLabel = true }: ProgressBarProps) {
    // 确保进度值在有效范围内
    const clampedProgress = Math.min(Math.max(progress, 0), 100);

    return (
        <div className="w-full">
            <div className="flex items-center gap-3">
                {/* 进度条轨道 */}
                <div className="flex-1 h-2 bg-slate-200/50 rounded-full overflow-hidden">
                    {/* 进度条填充 */}
                    <div
                        className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full transition-all duration-300 ease-out"
                        style={{ width: `${clampedProgress}%` }}
                    />
                </div>
                {/* 百分比标签 */}
                {showLabel && (
                    <span className="text-xs font-medium text-purple-600 w-10 text-right">
                        {Math.round(clampedProgress)}%
                    </span>
                )}
            </div>
        </div>
    );
}
