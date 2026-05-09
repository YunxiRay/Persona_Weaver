import { create } from "zustand";

export interface LLMConfig {
  provider: string;
  apiKey: string;
  model: string;
  baseUrl: string;
}

interface ConfigState {
  config: LLMConfig;
  isConfigured: boolean;
  setConfig: (config: Partial<LLMConfig>) => void;
  loadFromStorage: () => void;
  saveToStorage: () => void;
}

const STORAGE_KEY = "pw_llm_config";

const defaults: LLMConfig = {
  provider: "deepseek",
  apiKey: "",
  model: "deepseek-chat",
  baseUrl: "",
};

export const useConfigStore = create<ConfigState>((set, get) => ({
  config: { ...defaults },
  isConfigured: false,

  setConfig: (partial) => {
    const next = { ...get().config, ...partial };
    set({ config: next, isConfigured: !!next.apiKey });
    get().saveToStorage();
  },

  loadFromStorage: () => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        set({ config: { ...defaults, ...parsed }, isConfigured: !!parsed.apiKey });
      }
    } catch {
      // ignore
    }
  },

  saveToStorage: () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(get().config));
  },
}));
