import { describe, it, expect, beforeEach } from "vitest";
import { useChatStore } from "@/stores/chatStore";

describe("ChatStore", () => {
  beforeEach(() => {
    useChatStore.setState({
      messages: [],
      sessionId: null,
      phase: "RAPPORT",
      phaseLabel: "正在建立连接...",
      connectionStatus: "disconnected",
      mbtiHint: "",
      defenseFlags: [],
      isFinal: false,
      error: null,
    });
  });

  describe("addMessage", () => {
    it("appends message to empty list", () => {
      const msg = { id: "1", role: "user" as const, content: "你好", timestamp: 1000 };
      useChatStore.getState().addMessage(msg);
      expect(useChatStore.getState().messages).toHaveLength(1);
      expect(useChatStore.getState().messages[0].content).toBe("你好");
    });

    it("appends multiple messages in order", () => {
      useChatStore.getState().addMessage({ id: "1", role: "user" as const, content: "a", timestamp: 1 });
      useChatStore.getState().addMessage({ id: "2", role: "assistant" as const, content: "b", timestamp: 2 });
      expect(useChatStore.getState().messages).toHaveLength(2);
      expect(useChatStore.getState().messages[0].role).toBe("user");
      expect(useChatStore.getState().messages[1].role).toBe("assistant");
    });
  });

  describe("setPhase", () => {
    it("updates phase and label", () => {
      useChatStore.getState().setPhase("EXPLORATION", "深入探索");
      expect(useChatStore.getState().phase).toBe("EXPLORATION");
      expect(useChatStore.getState().phaseLabel).toBe("深入探索");
    });
  });

  describe("setConnectionStatus", () => {
    it("sets to connected", () => {
      useChatStore.getState().setConnectionStatus("connected");
      expect(useChatStore.getState().connectionStatus).toBe("connected");
    });

    it("sets to disconnected", () => {
      useChatStore.getState().setConnectionStatus("disconnected");
      expect(useChatStore.getState().connectionStatus).toBe("disconnected");
    });
  });

  describe("setSessionId", () => {
    it("stores session id", () => {
      useChatStore.getState().setSessionId("sess-123");
      expect(useChatStore.getState().sessionId).toBe("sess-123");
    });
  });

  describe("setMbtiHint", () => {
    it("stores mbti hint", () => {
      useChatStore.getState().setMbtiHint("INFJ");
      expect(useChatStore.getState().mbtiHint).toBe("INFJ");
    });
  });

  describe("setDefenseFlags", () => {
    it("stores defense flags", () => {
      useChatStore.getState().setDefenseFlags(["avoidance", "splitting"]);
      expect(useChatStore.getState().defenseFlags).toEqual(["avoidance", "splitting"]);
    });
  });

  describe("setIsFinal", () => {
    it("marks conversation as final", () => {
      expect(useChatStore.getState().isFinal).toBe(false);
      useChatStore.getState().setIsFinal(true);
      expect(useChatStore.getState().isFinal).toBe(true);
    });
  });

  describe("reset", () => {
    it("clears all state back to defaults", () => {
      useChatStore.getState().addMessage({ id: "1", role: "user" as const, content: "x", timestamp: 1 });
      useChatStore.getState().setSessionId("abc");
      useChatStore.getState().setPhase("CONFRONTATION", "对峙");
      useChatStore.getState().setMbtiHint("ENFP");
      useChatStore.getState().setIsFinal(true);

      useChatStore.getState().reset();

      expect(useChatStore.getState().messages).toEqual([]);
      expect(useChatStore.getState().sessionId).toBeNull();
      expect(useChatStore.getState().phase).toBe("RAPPORT");
      expect(useChatStore.getState().mbtiHint).toBe("");
      expect(useChatStore.getState().isFinal).toBe(false);
      expect(useChatStore.getState().error).toBeNull();
    });
  });
});
