interface AlgoMateLogoProps {
    size?: number;
    className?: string;
}

/**
 * AlgoMate Logo - ChatGPT 风格优化版
 * 六边形 + 交织线条，深蓝绿色调
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
                <linearGradient id="algoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#0891B2" />
                    <stop offset="100%" stopColor="#059669" />
                </linearGradient>
            </defs>

            {/* 六边形轮廓 */}
            <path
                d="M40 6 L69 22.5 L69 55.5 L40 72 L11 55.5 L11 22.5 Z"
                stroke="url(#algoGradient)"
                strokeWidth="3"
                fill="none"
            />

            {/* 交织线条 - 左 */}
            <path
                d="M40 22 L40 58"
                stroke="url(#algoGradient)"
                strokeWidth="3"
                strokeLinecap="round"
            />
            
            {/* 交织线条 - 右上 */}
            <path
                d="M40 30 L62 42.5 L62 55"
                stroke="url(#algoGradient)"
                strokeWidth="3"
                strokeLinecap="round"
                fill="none"
            />
            
            {/* 交织线条 - 右下 */}
            <path
                d="M40 46 L62 34 L62 22"
                stroke="url(#algoGradient)"
                strokeWidth="3"
                strokeLinecap="round"
                fill="none"
            />
            
            {/* 交织线条 - 左上 */}
            <path
                d="M40 30 L18 42.5 L18 55"
                stroke="url(#algoGradient)"
                strokeWidth="3"
                strokeLinecap="round"
                fill="none"
            />
            
            {/* 交织线条 - 左下 */}
            <path
                d="M40 46 L18 34 L18 22"
                stroke="url(#algoGradient)"
                strokeWidth="3"
                strokeLinecap="round"
                fill="none"
            />
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
                <linearGradient id="simpleAlgoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#0891B2" />
                    <stop offset="100%" stopColor="#059669" />
                </linearGradient>
            </defs>

            {/* 六边形 */}
            <path
                d="M16 4 L27 10 L27 22 L16 28 L5 22 L5 10 Z"
                stroke="url(#simpleAlgoGradient)"
                strokeWidth="2.5"
                fill="none"
            />

            {/* 三条交织线 */}
            <path
                d="M16 10 L16 22 M16 13 L26 19 M16 13 L6 19"
                stroke="url(#simpleAlgoGradient)"
                strokeWidth="2.5"
                strokeLinecap="round"
            />
        </svg>
    );
}
