import { Trash2 } from "lucide-react";

interface ActionButtonsProps {
    onClearMessages: () => void;
    disabled?: boolean;
}

export function ActionButtons({ onClearMessages, disabled }: ActionButtonsProps) {
    return (
        <button
            onClick={onClearMessages}
            disabled={disabled}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-red-50/80 hover:bg-red-100/80 disabled:opacity-50 disabled:cursor-not-allowed text-red-600 rounded-xl text-sm font-medium transition-all duration-200 border border-red-200/50"
        >
            <Trash2 className="w-4 h-4" />
            清空对话
        </button>
    );
}
