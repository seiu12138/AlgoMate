interface AlgoMateLogoProps {
    size?: number;
    className?: string;
}

/**
 * AlgoMate Logo - 黑白极简版
 * OpenAI/ChatGPT 风格，纯粹几何
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
            {/* 六边形轮廓 */}
            <path
                d="M40 6 L69 22.5 L69 55.5 L40 72 L11 55.5 L11 22.5 Z"
                stroke="currentColor"
                strokeWidth="3"
                fill="none"
            />

            {/* 三条交织线 */}
            <path
                d="M40 22 L40 58"
                stroke="currentColor"
                strokeWidth="3"
                strokeLinecap="round"
            />
            <path
                d="M40 30 L62 42.5 L62 55"
                stroke="currentColor"
                strokeWidth="3"
                strokeLinecap="round"
                fill="none"
            />
            <path
                d="M40 30 L18 42.5 L18 55"
                stroke="currentColor"
                strokeWidth="3"
                strokeLinecap="round"
                fill="none"
            />

            {/* 决策节点 */}
            <circle cx="40" cy="30" r="4" fill="currentColor" />
            <circle cx="18" cy="42.5" r="3" fill="currentColor" />
            <circle cx="62" cy="42.5" r="3" fill="currentColor" />
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
            {/* 六边形 */}
            <path
                d="M16 4 L27 10 L27 22 L16 28 L5 22 L5 10 Z"
                stroke="currentColor"
                strokeWidth="2.5"
                fill="none"
            />

            {/* 交织线 */}
            <path
                d="M16 10 L16 22 M16 14 L25 19 M16 14 L7 19"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
            />

            {/* 中心点 */}
            <circle cx="16" cy="14" r="2.5" fill="currentColor" />
        </svg>
    );
}
