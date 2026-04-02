/**
 * 状态徽章组件
 * 
 * 显示带有图标和文本的状态指示器。
 * 用于展示操作结果状态（成功、失败、进行中、等待中）。
 * 
 * @example
 * ```tsx
 * <StatusBadge status="success" text="执行成功" />
 * <StatusBadge status="pending" />
 * ```
 */

import { CheckCircle, XCircle, Loader2, Clock } from "lucide-react";

/** 状态类型 */
type StatusType = "success" | "error" | "pending" | "idle";

interface StatusBadgeProps {
    /** 状态类型 */
    status: StatusType;
    /** 自定义显示文本，如不传则使用默认文本 */
    text?: string;
}

/** 状态配置映射表 */
const statusConfig = {
    success: {
        icon: CheckCircle,
        className: "status-badge-success",
        defaultText: "成功",
    },
    error: {
        icon: XCircle,
        className: "status-badge-error",
        defaultText: "失败",
    },
    pending: {
        icon: Loader2,
        className: "status-badge-pending",
        defaultText: "处理中",
    },
    idle: {
        icon: Clock,
        className: "bg-gray-100 text-gray-600",
        defaultText: "等待中",
    },
};

/**
 * 状态徽章组件
 * 
 * 根据状态类型显示对应的图标和文本，支持动画效果。
 * 
 * @param status - 状态类型，决定颜色和图标
 * @param text - 可选的自定义文本
 */
export function StatusBadge({ status, text }: StatusBadgeProps) {
    const config = statusConfig[status];
    const Icon = config.icon;

    return (
        <span className={`status-badge ${config.className} ${status === "pending" ? "animate-pulse" : ""}`}>
            <Icon className={`w-3.5 h-3.5 mr-1 ${status === "pending" ? "animate-spin" : ""}`} />
            {text || config.defaultText}
        </span>
    );
}
