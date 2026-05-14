import { create } from "zustand";

export interface PatternRef {
  id: string;
  name: string;
  category: string;
  score: number;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: number;
  phase?: string;
  patternReferences?: PatternRef[];
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
  errorHint: string | null;
  turn: number;
  currentPatternRefs: PatternRef[];

  addMessage: (msg: ChatMessage) => void;
  updateLastAssistant: (content: string) => void;
  setSessionId: (id: string) => void;
  setPhase: (phase: string, label: string) => void;
  setConnectionStatus: (status: "connecting" | "connected" | "disconnected") => void;
  setMbtiHint: (hint: string) => void;
  setDefenseFlags: (flags: string[]) => void;
  setIsFinal: (final: boolean) => void;
  setError: (err: string | null) => void;
  setErrorHint: (hint: string | null) => void;
  setTurn: (turn: number) => void;
  setCurrentPatternRefs: (refs: PatternRef[]) => void;
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
  errorHint: null,
  turn: 0,
  currentPatternRefs: [],

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
  setErrorHint: (hint) => set({ errorHint: hint }),
  setTurn: (turn) => set({ turn }),
  setCurrentPatternRefs: (refs) => set({ currentPatternRefs: refs }),
  reset: () => set({
    messages: [], sessionId: null, phase: "RAPPORT", phaseLabel: "正在建立连接...",
    mbtiHint: "", defenseFlags: [], isFinal: false, error: null, errorHint: null, turn: 0,
    currentPatternRefs: [],
  }),
}));
