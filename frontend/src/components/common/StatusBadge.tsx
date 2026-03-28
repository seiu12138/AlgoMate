import { CheckCircle, XCircle, Loader2, Clock } from "lucide-react";

type StatusType = "success" | "error" | "pending" | "idle";

interface StatusBadgeProps {
    status: StatusType;
    text?: string;
}

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
