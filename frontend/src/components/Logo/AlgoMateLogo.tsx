interface AlgoMateLogoProps {
    size?: number;
    className?: string;
}

/**
 * AlgoMate Logo - ChatGPT 风格
 * 六边形交织结构，代表算法与神经网络的融合
 */
export function AlgoMateLogo({ size = 80, className = "" }: AlgoMateLogoProps) {
    return (
        <svg
            width={size}
            height={size}
            viewBox="0 0 80 80"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className={className}
        >
            <defs>
                <linearGradient id="aiGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#10B981" />
                    <stop offset="100%" stopColor="#3B82F6" />
                </linearGradient>
                <linearGradient id="aiGradientAlt" x1="0%" y1="100%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#3B82F6" />
                    <stop offset="100%" stopColor="#10B981" />
                </linearGradient>
            </defs>

            {/* 外六边形轮廓 */}
            <path
                d="M40 5 L67.5 20 L67.5 52.5 L40 67.5 L12.5 52.5 L12.5 20 Z"
                stroke="url(#aiGradient)"
                strokeWidth="2.5"
                fill="none"
                opacity="0.9"
            />

            {/* 内部交织结构 - 类似神经网络 */}
            {/* 垂直主线 */}
            <line x1="40" y1="15" x2="40" y2="57.5" stroke="url(#aiGradient)" strokeWidth="2.5" strokeLinecap="round" />
            
            {/* 左斜线 */}
            <line x1="40" y1="25" x2="22" y2="35" stroke="url(#aiGradientAlt)" strokeWidth="2.5" strokeLinecap="round" />
            <line x1="22" y1="35" x2="22" y2="47.5" stroke="url(#aiGradientAlt)" strokeWidth="2.5" strokeLinecap="round" />
            
            {/* 右斜线 */}
            <line x1="40" y1="25" x2="58" y2="35" stroke="url(#aiGradientAlt)" strokeWidth="2.5" strokeLinecap="round" />
            <line x1="58" y1="35" x2="58" y2="47.5" stroke="url(#aiGradientAlt)" strokeWidth="2.5" strokeLinecap="round" />

            {/* 连接线 - 形成网络 */}
            <line x1="22" y1="47.5" x2="40" y2="57.5" stroke="url(#aiGradient)" strokeWidth="2.5" strokeLinecap="round" />
            <line x1="58" y1="47.5" x2="40" y2="57.5" stroke="url(#aiGradient)" strokeWidth="2.5" strokeLinecap="round" />

            {/* 中心节点 */}
            <circle cx="40" cy="36.25" r="6" fill="url(#aiGradient)" />
            
            {/* 外围节点 */}
            <circle cx="40" cy="15" r="3.5" fill="#10B981" />
            <circle cx="22" cy="35" r="3.5" fill="#3B82F6" />
            <circle cx="22" cy="47.5" r="3.5" fill="#10B981" />
            <circle cx="58" cy="35" r="3.5" fill="#3B82F6" />
            <circle cx="58" cy="47.5" r="3.5" fill="#10B981" />
            <circle cx="40" cy="57.5" r="3.5" fill="#3B82F6" />
        </svg>
    );
}

/**
 * 简化版 - Sidebar
 */
export function AlgoMateLogoSimple({ size = 32, className = "" }: AlgoMateLogoProps) {
    return (
        <svg
            width={size}
            height={size}
            viewBox="0 0 32 32"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className={className}
        >
            <defs>
                <linearGradient id="simpleAiGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#10B981" />
                    <stop offset="100%" stopColor="#3B82F6" />
                </linearGradient>
            </defs>

            {/* 六边形 */}
            <path
                d="M16 4 L26.5 10 L26.5 22 L16 28 L5.5 22 L5.5 10 Z"
                stroke="url(#simpleAiGradient)"
                strokeWidth="2"
                fill="none"
            />

            {/* 中心交织 */}
            <path
                d="M16 10 L16 22 M16 14 L11 17 L11 21 M16 14 L21 17 L21 21"
                stroke="url(#simpleAiGradient)"
                strokeWidth="2"
                strokeLinecap="round"
            />

            {/* 中心点 */}
            <circle cx="16" cy="16" r="3" fill="url(#simpleAiGradient)" />
        </svg>
    );
}
