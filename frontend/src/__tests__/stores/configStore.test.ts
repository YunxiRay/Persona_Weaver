import { describe, it, expect, beforeEach, vi } from "vitest";
import { useConfigStore } from "@/stores/configStore";

describe("ConfigStore", () => {
  beforeEach(() => {
    useConfigStore.setState({
      config: {
        provider: "deepseek",
        apiKey: "",
        model: "deepseek-chat",
        baseUrl: "",
      },
      isConfigured: false,
    });
    localStorage.clear();
  });

  describe("initial state", () => {
    it("has deepseek as default provider", () => {
      expect(useConfigStore.getState().config.provider).toBe("deepseek");
    });

    it("is not configured by default", () => {
      expect(useConfigStore.getState().isConfigured).toBe(false);
    });
  });

  describe("setConfig", () => {
    it("updates provider and auto-fills model", () => {
      useConfigStore.getState().setConfig({ provider: "qwen", model: "qwen-plus" });
      expect(useConfigStore.getState().config.provider).toBe("qwen");
      expect(useConfigStore.getState().config.model).toBe("qwen-plus");
    });

    it("sets isConfigured when apiKey is provided", () => {
      useConfigStore.getState().setConfig({ apiKey: "sk-test-key" });
      expect(useConfigStore.getState().isConfigured).toBe(true);
      expect(useConfigStore.getState().config.apiKey).toBe("sk-test-key");
    });

    it("persists to localStorage", () => {
      useConfigStore.getState().setConfig({ apiKey: "sk-persist", model: "gpt-4" });
      const stored = JSON.parse(localStorage.getItem("pw_llm_config") || "{}");
      expect(stored.apiKey).toBe("sk-persist");
      expect(stored.model).toBe("gpt-4");
    });

    it("merges partial config with existing values", () => {
      useConfigStore.getState().setConfig({ apiKey: "sk-abc" });
      useConfigStore.getState().setConfig({ model: "new-model" });
      expect(useConfigStore.getState().config.apiKey).toBe("sk-abc");
      expect(useConfigStore.getState().config.model).toBe("new-model");
      expect(useConfigStore.getState().config.provider).toBe("deepseek");
    });
  });

  describe("loadFromStorage", () => {
    it("loads previously saved config", () => {
      localStorage.setItem("pw_llm_config", JSON.stringify({
        provider: "moonshot",
        apiKey: "sk-loaded",
        model: "moonshot-v1-8k",
        baseUrl: "https://api.moonshot.cn/v1",
      }));

      useConfigStore.getState().loadFromStorage();

      expect(useConfigStore.getState().config.provider).toBe("moonshot");
      expect(useConfigStore.getState().config.apiKey).toBe("sk-loaded");
      expect(useConfigStore.getState().isConfigured).toBe(true);
    });

    it("handles empty storage gracefully", () => {
      useConfigStore.getState().loadFromStorage();
      expect(useConfigStore.getState().config.provider).toBe("deepseek");
      expect(useConfigStore.getState().isConfigured).toBe(false);
    });

    it("handles corrupt storage gracefully", () => {
      localStorage.setItem("pw_llm_config", "not-valid-json");
      expect(() => useConfigStore.getState().loadFromStorage()).not.toThrow();
    });
  });
});
