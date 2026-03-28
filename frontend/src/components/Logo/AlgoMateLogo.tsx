interface AlgoMateLogoProps {
    size?: number;
    className?: string;
}

/**
 * AlgoMate Logo - 算法与学习融合
 * 六边形 + 交织线 + 决策树节点 + 成长阶梯
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
                <linearGradient id="algoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#0891B2" />
                    <stop offset="100%" stopColor="#059669" />
                </linearGradient>
            </defs>

            {/* 六边形轮廓 */}
            <path
                d="M40 6 L69 22.5 L69 55.5 L40 72 L11 55.5 L11 22.5 Z"
                stroke="url(#algoGrad)"
                strokeWidth="3"
                fill="none"
            />

            {/* 三条主交织线 */}
            <path
                d="M40 22 L40 58"
                stroke="url(#algoGrad)"
                strokeWidth="3"
                strokeLinecap="round"
            />
            <path
                d="M40 30 L62 42.5 L62 55"
                stroke="url(#algoGrad)"
                strokeWidth="3"
                strokeLinecap="round"
                fill="none"
            />
            <path
                d="M40 30 L18 42.5 L18 55"
                stroke="url(#algoGrad)"
                strokeWidth="3"
                strokeLinecap="round"
                fill="none"
            />

            {/* 决策节点 - 算法决策点 */}
            <circle cx="40" cy="30" r="4" fill="#0891B2" />
            <circle cx="18" cy="42.5" r="3" fill="#10B981" />
            <circle cx="62" cy="42.5" r="3" fill="#10B981" />

            {/* 向上阶梯 - 学习成长 */}
            <path
                d="M28 62 L32 62 L32 58 L36 58 L36 54 L40 54"
                stroke="url(#algoGrad)"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                fill="none"
                opacity="0.8"
            />

            {/* 底部节点 - 终点/目标 */}
            <circle cx="40" cy="54" r="2.5" fill="#059669" />
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
                <linearGradient id="simpleAlgoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#0891B2" />
                    <stop offset="100%" stopColor="#059669" />
                </linearGradient>
            </defs>

            {/* 六边形 */}
            <path
                d="M16 4 L27 10 L27 22 L16 28 L5 22 L5 10 Z"
                stroke="url(#simpleAlgoGrad)"
                strokeWidth="2.5"
                fill="none"
            />

            {/* 交织线 + 节点 */}
            <path
                d="M16 10 L16 22 M16 14 L25 19 M16 14 L7 19"
                stroke="url(#simpleAlgoGrad)"
                strokeWidth="2.5"
                strokeLinecap="round"
            />

            {/* 中心决策点 */}
            <circle cx="16" cy="14" r="2.5" fill="#0891B2" />
        </svg>
    );
}
