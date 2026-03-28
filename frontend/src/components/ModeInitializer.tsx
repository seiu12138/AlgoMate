import { useEffect, useRef } from "react";
import { useChatStore } from "../stores/chatStore";

/**
 * ModeInitializer handles automatic session loading when mode changes
 * This is a headless component that doesn't render anything
 */
export function ModeInitializer() {
    const { mode, loadSessions, loadRecentSession, currentSessionId } = useChatStore();
    const initialized = useRef(false);
    const prevMode = useRef(mode);

    // Initial load
    useEffect(() => {
        if (!initialized.current) {
            loadSessions();
            initialized.current = true;
        }
    }, [loadSessions]);

    // Handle mode change - load recent session for new mode
    useEffect(() => {
        if (initialized.current && prevMode.current !== mode) {
            // When mode changes, load the most recent session for that mode
            // or create a new one if none exists
            loadRecentSession(mode);
            prevMode.current = mode;
        }
    }, [mode, loadRecentSession]);

    return null;
}
