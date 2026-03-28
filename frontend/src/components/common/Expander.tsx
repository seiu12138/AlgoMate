import { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";

interface ExpanderProps {
    title: React.ReactNode;
    children: React.ReactNode;
    defaultExpanded?: boolean;
    headerClassName?: string;
    contentClassName?: string;
}

export function Expander({
    title,
    children,
    defaultExpanded = false,
    headerClassName = "",
    contentClassName = "",
}: ExpanderProps) {
    const [isExpanded, setIsExpanded] = useState(defaultExpanded);

    return (
        <div className="border border-slate-200/50 rounded-xl overflow-hidden bg-white/40 backdrop-blur-sm">
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className={`w-full flex items-center justify-between px-4 py-3 hover:bg-white/60 transition-colors ${headerClassName}`}
            >
                <div className="flex items-center gap-2">{title}</div>
                {isExpanded ? (
                    <ChevronDown className="w-4 h-4 text-gray-400" />
                ) : (
                    <ChevronRight className="w-4 h-4 text-gray-400" />
                )}
            </button>
            {isExpanded && (
                <div className={`px-4 pb-4 animate-fade-in ${contentClassName}`}>
                    {children}
                </div>
            )}
        </div>
    );
}
