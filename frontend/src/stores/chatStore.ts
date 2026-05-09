import { create } from "zustand";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: number;
  phase?: string;
}

interface ChatState {
  messages: ChatMessage[];
  sessionId: string | null;
  phase: string;
  phaseLabel: string;
  connectionStatus: "connecting" | "connected" | "disconnected";
  mbtiHint: string;
  defenseFlags: string[];
  isFinal: boolean;
  error: string | null;

  addMessage: (msg: ChatMessage) => void;
  updateLastAssistant: (content: string) => void;
  setSessionId: (id: string) => void;
  setPhase: (phase: string, label: string) => void;
  setConnectionStatus: (status: "connecting" | "connected" | "disconnected") => void;
  setMbtiHint: (hint: string) => void;
  setDefenseFlags: (flags: string[]) => void;
  setIsFinal: (final: boolean) => void;
  setError: (err: string | null) => void;
  reset: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  sessionId: null,
  phase: "RAPPORT",
  phaseLabel: "正在建立连接...",
  connectionStatus: "disconnected",
  mbtiHint: "",
  defenseFlags: [],
  isFinal: false,
  error: null,

  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
  updateLastAssistant: (content) => set((s) => {
    const msgs = [...s.messages];
    for (let i = msgs.length - 1; i >= 0; i--) {
      if (msgs[i].role === "assistant") { msgs[i] = { ...msgs[i], content }; break; }
    }
    return { messages: msgs };
  }),
  setSessionId: (id) => set({ sessionId: id }),
  setPhase: (phase, label) => set({ phase, phaseLabel: label }),
  setConnectionStatus: (status) => set({ connectionStatus: status }),
  setMbtiHint: (hint) => set({ mbtiHint: hint }),
  setDefenseFlags: (flags) => set({ defenseFlags: flags }),
  setIsFinal: (final) => set({ isFinal: final }),
  setError: (err) => set({ error: err }),
  reset: () => set({
    messages: [], sessionId: null, phase: "RAPPORT", phaseLabel: "正在建立连接...",
    mbtiHint: "", defenseFlags: [], isFinal: false, error: null,
  }),
}));
