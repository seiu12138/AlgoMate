interface AlgoMateLogoProps {
    size?: number;
    className?: string;
}

/**
 * AlgoMate Agent Logo - 体现智能 Agent 特性
 * 融合：AI大脑 + 工具执行 + 代码编程 + ReAct循环
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
                {/* 主渐变 - 科技感 */}
                <linearGradient id="agentGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#06B6D4" /> {/* 青色 - 智能 */}
                    <stop offset="50%" stopColor="#8B5CF6" /> {/* 紫色 - 神秘/AI */}
                    <stop offset="100%" stopColor="#EC4899" /> {/* 粉色 - 活力 */}
                </linearGradient>
                
                {/* 大脑渐变 */}
                <linearGradient id="brainGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor="#F0F9FF" />
                    <stop offset="100%" stopColor="#E0F2FE" />
                </linearGradient>

                {/* 发光效果 */}
                <filter id="agentGlow" x="-50%" y="-50%" width="200%" height="200%">
                    <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                    <feMerge>
                        <feMergeNode in="coloredBlur"/>
                        <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                </filter>
            </defs>

            {/* 外圈 - ReAct 循环箭头 */}
            <path
                d="M40 5 A35 35 0 0 1 75 40"
                stroke="url(#agentGradient)"
                strokeWidth="3"
                strokeLinecap="round"
                fill="none"
                opacity="0.6"
            />
            <path
                d="M75 40 A35 35 0 0 1 40 75"
                stroke="url(#agentGradient)"
                strokeWidth="3"
                strokeLinecap="round"
                fill="none"
                opacity="0.8"
            />
            <path
                d="M40 75 A35 35 0 0 1 5 40"
                stroke="url(#agentGradient)"
                strokeWidth="3"
                strokeLinecap="round"
                fill="none"
                opacity="1"
            />
            <path
                d="M5 40 A35 35 0 0 1 40 5"
                stroke="url(#agentGradient)"
                strokeWidth="3"
                strokeLinecap="round"
                fill="none"
                opacity="0.4"
            />
            
            {/* 循环箭头头部 */}
            <polygon points="40,2 44,8 36,8" fill="#06B6D4" />

            {/* Agent 核心 - 六边形大脑 */}
            <path
                d="M40 18 L52 25 L52 39 L40 46 L28 39 L28 25 Z"
                fill="url(#brainGradient)"
                stroke="url(#agentGradient)"
                strokeWidth="2"
                filter="url(#agentGlow)"
            />

            {/* 大脑内部 - 神经网络节点 */}
            <circle cx="40" cy="28" r="3" fill="#8B5CF6" />
            <circle cx="35" cy="33" r="2.5" fill="#06B6D4" />
            <circle cx="45" cy="33" r="2.5" fill="#EC4899" />
            <circle cx="40" cy="38" r="2" fill="#8B5CF6" />

            {/* 神经连接 */}
            <path d="M40 28 L35 33" stroke="#CBD5E1" strokeWidth="1" />
            <path d="M40 28 L45 33" stroke="#CBD5E1" strokeWidth="1" />
            <path d="M35 33 L40 38" stroke="#CBD5E1" strokeWidth="1" />
            <path d="M45 33 L40 38" stroke="#CBD5E1" strokeWidth="1" />

            {/* 工具图标 - 扳手（左） */}
            <g transform="translate(14, 50)">
                <path
                    d="M2 2 L6 6 M6 2 L2 6"
                    stroke="#06B6D4"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                />
                <circle cx="4" cy="4" r="5" stroke="#06B6D4" strokeWidth="1.5" fill="none" opacity="0.3" />
            </g>

            {/* 工具图标 - 代码符号（右） */}
            <g transform="translate(58, 50)">
                <path d="M2 2 L0 4 L2 6" stroke="#EC4899" strokeWidth="2" strokeLinecap="round" fill="none" />
                <path d="M6 2 L8 4 L6 6" stroke="#EC4899" strokeWidth="2" strokeLinecap="round" fill="none" />
                <line x1="3" y1="7" x2="5" y2="1" stroke="#EC4899" strokeWidth="1.5" strokeLinecap="round" />
            </g>

            {/* 底部文字 - Agent */}
            <text 
                x="40" 
                y="72" 
                fontSize="6" 
                fill="#64748B" 
                textAnchor="middle" 
                fontFamily="system-ui, sans-serif"
                fontWeight="600"
                letterSpacing="1"
            >
                AGENT
            </text>
        </svg>
    );
}

/**
 * 简化版 Logo - 用于 Sidebar 等小尺寸场景
 * 突出 Agent 核心特征：大脑 + 循环
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
                <linearGradient id="simpleAgentGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#06B6D4" />
                    <stop offset="100%" stopColor="#8B5CF6" />
                </linearGradient>
            </defs>

            {/* 简化循环箭头 */}
            <path
                d="M16 4 A12 12 0 0 1 28 16"
                stroke="url(#simpleAgentGradient)"
                strokeWidth="2.5"
                strokeLinecap="round"
                fill="none"
            />
            <path
                d="M28 16 A12 12 0 0 1 16 28"
                stroke="url(#simpleAgentGradient)"
                strokeWidth="2.5"
                strokeLinecap="round"
                fill="none"
                opacity="0.7"
            />
            <path
                d="M16 28 A12 12 0 0 1 4 16"
                stroke="url(#simpleAgentGradient)"
                strokeWidth="2.5"
                strokeLinecap="round"
                fill="none"
                opacity="0.4"
            />

            {/* 中心 Agent 核心 */}
            <circle cx="16" cy="16" r="5" fill="white" stroke="url(#simpleAgentGradient)" strokeWidth="2" />
            
            {/* 核心点 */}
            <circle cx="16" cy="16" r="2" fill="url(#simpleAgentGradient)" />
        </svg>
    );
}

/**
 * 极简版 - 纯图标，用于 Favicon
 */
export function AlgoMateLogoMinimal({ size = 16 }: AlgoMateLogoProps) {
    return (
        <svg
            width={size}
            height={size}
            viewBox="0 0 16 16"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
        >
            {/* 六边形 Agent 核心 */}
            <path
                d="M8 2 L13 5 L13 11 L8 14 L3 11 L3 5 Z"
                fill="url(#simpleAgentGradient)"
            />
            {/* 中心 */}
            <circle cx="8" cy="9" r="2" fill="white" />
        </svg>
    );
}
