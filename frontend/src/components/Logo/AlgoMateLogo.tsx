interface AlgoMateLogoProps {
    size?: number;
    className?: string;
}

/**
 * AlgoMate Logo - 学习 × AI × 算法
 * 核心概念：AI 导师带领学习算法，点亮思维
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
                {/* 智慧蓝渐变 */}
                <linearGradient id="learnGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#3B82F6" />
                    <stop offset="50%" stopColor="#6366F1" />
                    <stop offset="100%" stopColor="#8B5CF6" />
                </linearGradient>
                
                {/* 灵光渐变 */}
                <radialGradient id="glowGradient" cx="50%" cy="30%" r="50%">
                    <stop offset="0%" stopColor="#FEF3C7" />
                    <stop offset="100%" stopColor="#F59E0B" />
                </radialGradient>

                {/* 柔和发光 */}
                <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%">
                    <feGaussianBlur stdDeviation="2" result="blur"/>
                    <feComposite in="SourceGraphic" in2="blur" operator="over"/>
                </filter>
            </defs>

            {/* 书本底座 - 知识基础 */}
            <path
                d="M20 55 L20 62 Q20 66 25 66 L55 66 Q60 66 60 62 L60 55 Q60 58 55 58 L25 58 Q20 58 20 55 Z"
                fill="url(#learnGradient)"
                opacity="0.9"
            />
            <path
                d="M20 55 Q20 51 25 51 L55 51 Q60 51 60 55 L60 58 Q60 62 55 62 L25 62 Q20 62 20 58 Z"
                fill="url(#learnGradient)"
            />
            {/* 书页线条 */}
            <line x1="28" y1="54" x2="52" y2="54" stroke="white" strokeWidth="1.5" opacity="0.6" strokeLinecap="round"/>
            <line x1="28" y1="57" x2="48" y2="57" stroke="white" strokeWidth="1.5" opacity="0.4" strokeLinecap="round"/>

            {/* AI 导师 - 圆形头部 */}
            <circle cx="40" cy="35" r="14" fill="#F8FAFC" stroke="url(#learnGradient)" strokeWidth="2.5"/>
            
            {/* 眼睛 - 专注学习的眼神 */}
            <ellipse cx="35" cy="33" rx="3" ry="3.5" fill="#1E293B"/>
            <ellipse cx="45" cy="33" rx="3" ry="3.5" fill="#1E293B"/>
            {/* 眼神光点 */}
            <circle cx="36" cy="32" r="1" fill="white"/>
            <circle cx="46" cy="32" r="1" fill="white"/>
            
            {/* 微笑 - 友好导师 */}
            <path d="M35 40 Q40 44, 45 40" stroke="#1E293B" strokeWidth="1.5" strokeLinecap="round" fill="none"/>

            {/* 灵光/灯泡 - 思维启发 */}
            <g transform="translate(40, 14)">
                {/* 光芒 */}
                <line x1="0" y1="-8" x2="0" y2="-4" stroke="#F59E0B" strokeWidth="2" strokeLinecap="round"/>
                <line x1="-6" y1="-6" x2="-3" y2="-3" stroke="#F59E0B" strokeWidth="2" strokeLinecap="round"/>
                <line x1="6" y1="-6" x2="3" y2="-3" stroke="#F59E0B" strokeWidth="2" strokeLinecap="round"/>
                
                {/* 灯泡 */}
                <circle cx="0" cy="0" r="4" fill="url(#glowGradient)" filter="url(#softGlow)"/>
            </g>

            {/* 算法符号 - 代码片段 */}
            <g transform="translate(52, 38)">
                <text x="0" y="0" fontSize="8" fill="#6366F1" fontFamily="monospace" fontWeight="bold">&lt;/&gt;</text>
            </g>

            {/* 左侧装饰 - 二进制/数据流 */}
            <g transform="translate(18, 35)">
                <rect x="0" y="0" width="3" height="3" fill="#3B82F6" opacity="0.8"/>
                <rect x="0" y="5" width="3" height="3" fill="#3B82F6" opacity="0.5"/>
                <rect x="4" y="2" width="3" height="3" fill="#3B82F6" opacity="0.3"/>
            </g>

            {/* 底部标签 */}
            <text 
                x="40" 
                y="76" 
                fontSize="5" 
                fill="#64748B" 
                textAnchor="middle" 
                fontFamily="system-ui, sans-serif"
                fontWeight="600"
                letterSpacing="0.5"
            >
                LEARN · CODE · SOLVE
            </text>
        </svg>
    );
}

/**
 * 简化版 Logo - Sidebar 使用
 * 书本 + AI 脸 + 灵光
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
                <linearGradient id="simpleLearnGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#3B82F6" />
                    <stop offset="100%" stopColor="#8B5CF6" />
                </linearGradient>
            </defs>

            {/* 书本 */}
            <path
                d="M6 22 L6 26 Q6 28 9 28 L23 28 Q26 28 26 26 L26 22"
                stroke="url(#simpleLearnGradient)"
                strokeWidth="2.5"
                strokeLinecap="round"
                fill="none"
            />
            <path
                d="M6 22 Q6 20 9 20 L23 20 Q26 20 26 22"
                stroke="url(#simpleLearnGradient)"
                strokeWidth="2.5"
                strokeLinecap="round"
                fill="none"
            />

            {/* AI 脸 */}
            <circle cx="16" cy="14" r="6" fill="white" stroke="url(#simpleLearnGradient)" strokeWidth="2"/>
            <circle cx="14" cy="13" r="1.5" fill="#1E293B"/>
            <circle cx="18" cy="13" r="1.5" fill="#1E293B"/>
            <path d="M13 17 Q16 19, 19 17" stroke="#1E293B" strokeWidth="1" strokeLinecap="round" fill="none"/>

            {/* 灵光 */}
            <circle cx="16" cy="5" r="2" fill="#F59E0B"/>
            <line x1="16" y1="2" x2="16" y2="3" stroke="#F59E0B" strokeWidth="1.5" strokeLinecap="round"/>
        </svg>
    );
}
