import { create } from "zustand";
import type { Language, AgentConfig } from "../types";

interface ConfigState extends AgentConfig {
    setLanguage: (language: Language) => void;
    setMaxIterations: (maxIterations: number) => void;
}

export const useConfigStore = create<ConfigState>((set) => ({
    language: "python",
    maxIterations: 5,
    setLanguage: (language) => set({ language }),
    setMaxIterations: (maxIterations) => set({ maxIterations }),
}));
