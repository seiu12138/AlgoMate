interface AlgoMateLogoProps {
    size?: number;
    className?: string;
}

/**
 * AlgoMate Logo - 专业简洁版
 * 核心概念：算法决策树 + 深度学习网络
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
                {/* 专业蓝灰渐变 */}
                <linearGradient id="proGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#0F172A" />
                    <stop offset="50%" stopColor="#1E3A5F" />
                    <stop offset="100%" stopColor="#3B82F6" />
                </linearGradient>
                
                {/* 节点渐变 */}
                <radialGradient id="nodeGradient" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stopColor="#60A5FA" />
                    <stop offset="100%" stopColor="#3B82F6" />
                </radialGradient>

                {/* 连接线渐变 */}
                <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#1E3A5F" />
                    <stop offset="100%" stopColor="#60A5FA" />
                </linearGradient>
            </defs>

            {/* 外框 - 六边形，象征稳定和结构 */}
            <path
                d="M40 8 L64 20 L64 52 L40 64 L16 52 L16 20 Z"
                stroke="url(#proGradient)"
                strokeWidth="2"
                fill="none"
                opacity="0.3"
            />

            {/* 决策树/算法结构 */}
            {/* 根节点 */}
            <circle cx="40" cy="20" r="5" fill="url(#proGradient)" />
            
            {/* 第一层分支 */}
            <line x1="40" y1="25" x2="28" y2="36" stroke="url(#lineGradient)" strokeWidth="2" />
            <line x1="40" y1="25" x2="52" y2="36" stroke="url(#lineGradient)" strokeWidth="2" />
            
            {/* 第一层节点 */}
            <circle cx="28" cy="36" r="4" fill="url(#nodeGradient)" />
            <circle cx="52" cy="36" r="4" fill="url(#nodeGradient)" />

            {/* 第二层分支 */}
            <line x1="28" y1="40" x2="22" y2="50" stroke="url(#lineGradient)" strokeWidth="1.5" />
            <line x1="28" y1="40" x2="34" y2="50" stroke="url(#lineGradient)" strokeWidth="1.5" />
            <line x1="52" y1="40" x2="46" y2="50" stroke="url(#lineGradient)" strokeWidth="1.5" />
            <line x1="52" y1="40" x2="58" y2="50" stroke="url(#lineGradient)" strokeWidth="1.5" />

            {/* 第二层节点 - 叶子节点 */}
            <circle cx="22" cy="50" r="3" fill="#60A5FA" />
            <circle cx="34" cy="50" r="3" fill="#60A5FA" />
            <circle cx="46" cy="50" r="3" fill="#60A5FA" />
            <circle cx="58" cy="50" r="3" fill="#60A5FA" />

            {/* 中央 A 字母 - 抽象几何 */}
            <path
                d="M40 30 L34 44 L36 44 L38 40 L42 40 L44 44 L46 44 L40 30 Z M39 38 L40 34 L41 38 L39 38 Z"
                fill="#0F172A"
            />

            {/* 底部装饰线 */}
            <line x1="25" y1="58" x2="55" y2="58" stroke="#3B82F6" strokeWidth="1" opacity="0.5" />
        </svg>
    );
}

/**
 * 简化版 Logo - Sidebar
 * 六边形 + 中心 A
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
                <linearGradient id="simpleProGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#1E3A5F" />
                    <stop offset="100%" stopColor="#3B82F6" />
                </linearGradient>
            </defs>

            {/* 六边形外框 */}
            <path
                d="M16 4 L26 9 L26 23 L16 28 L6 23 L6 9 Z"
                stroke="url(#simpleProGradient)"
                strokeWidth="2"
                fill="none"
            />

            {/* 中心 A */}
            <path
                d="M16 10 L13 20 H15 L15.5 18 H18.5 L19 20 H21 L18 10 H16 Z M16 16 L16.5 14 H17.5 L18 16 H16 Z"
                fill="url(#simpleProGradient)"
            />
        </svg>
    );
}
