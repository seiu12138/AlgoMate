interface ProgressBarProps {
    progress: number; // 0-100
    showLabel?: boolean;
}

export function ProgressBar({ progress, showLabel = true }: ProgressBarProps) {
    const clampedProgress = Math.min(Math.max(progress, 0), 100);

    return (
        <div className="w-full">
            <div className="flex items-center gap-3">
                <div className="flex-1 h-2 bg-slate-200/50 rounded-full overflow-hidden">
                    <div
                        className="h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full transition-all duration-300 ease-out"
                        style={{ width: `${clampedProgress}%` }}
                    />
                </div>
                {showLabel && (
                    <span className="text-xs font-medium text-purple-600 w-10 text-right">
                        {Math.round(clampedProgress)}%
                    </span>
                )}
            </div>
        </div>
    );
}
