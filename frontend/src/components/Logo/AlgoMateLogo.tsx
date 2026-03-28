interface AlgoMateLogoProps {
    size?: number;
    className?: string;
}

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
            {/* 背景渐变 */}
            <defs>
                <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#3B82F6" />
                    <stop offset="50%" stopColor="#8B5CF6" />
                    <stop offset="100%" stopColor="#A855F7" />
                </linearGradient>
                <linearGradient id="faceGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor="#F8FAFC" />
                    <stop offset="100%" stopColor="#E2E8F0" />
                </linearGradient>
                <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="2" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
            </defs>

            {/* 外框 - 代码括号形状 */}
            <path
                d="M20 15 
                   C 15 15, 10 20, 10 28
                   L 10 52
                   C 10 60, 15 65, 20 65
                   L 25 65
                   L 25 58
                   L 22 58
                   C 19 58, 17 55, 17 52
                   L 17 28
                   C 17 25, 19 22, 22 22
                   L 25 22
                   L 25 15
                   Z"
                fill="url(#logoGradient)"
                opacity="0.9"
            />
            <path
                d="M60 15 
                   C 65 15, 70 20, 70 28
                   L 70 52
                   C 70 60, 65 65, 60 65
                   L 55 65
                   L 55 58
                   L 58 58
                   C 61 58, 63 55, 63 52
                   L 63 28
                   C 63 25, 61 22, 58 22
                   L 55 22
                   L 55 15
                   Z"
                fill="url(#logoGradient)"
                opacity="0.9"
            />

            {/* 中间圆形 - 机器人脸部 */}
            <circle cx="40" cy="40" r="16" fill="url(#faceGradient)" stroke="url(#logoGradient)" strokeWidth="2" />

            {/* 眼睛 */}
            <rect x="32" y="36" width="6" height="4" rx="1" fill="#3B82F6" />
            <rect x="42" y="36" width="6" height="4" rx="1" fill="#3B82F6" />

            {/* 嘴巴 - 微笑 */}
            <path
                d="M34 46 Q 40 49, 46 46"
                stroke="#64748B"
                strokeWidth="1.5"
                strokeLinecap="round"
                fill="none"
            />

            {/* 天线 */}
            <line x1="40" y1="24" x2="40" y2="18" stroke="url(#logoGradient)" strokeWidth="2" strokeLinecap="round" />
            <circle cx="40" cy="16" r="2" fill="#F59E0B" />

            {/* 代码符号点缀 */}
            <text x="40" y="76" fontSize="6" fill="#94A3B8" textAnchor="middle" fontFamily="monospace">
                {"</>"}
            </text>
        </svg>
    );
}

// 简化版 Logo - 用于 favicon 或小尺寸显示
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
                <linearGradient id="simpleGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#3B82F6" />
                    <stop offset="100%" stopColor="#8B5CF6" />
                </linearGradient>
            </defs>
            
            {/* 代码括号 */}
            <path d="M6 8 L2 16 L6 24" stroke="url(#simpleGradient)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" fill="none" />
            <path d="M26 8 L30 16 L26 24" stroke="url(#simpleGradient)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" fill="none" />
            
            {/* 中间代码符号 */}
            <text x="16" y="19" fontSize="10" fill="url(#simpleGradient)" textAnchor="middle" fontFamily="monospace" fontWeight="bold">
                A
            </text>
        </svg>
    );
}
