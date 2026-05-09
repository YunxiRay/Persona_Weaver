import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ChatBubble } from "@/components/chat/ChatBubble";
import { ChatInput } from "@/components/chat/ChatInput";
import { PhaseIndicator } from "@/components/chat/PhaseIndicator";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useChatStore } from "@/stores/chatStore";
import { useConfigStore } from "@/stores/configStore";

export default function Chat() {
  const navigate = useNavigate();
  const { send, on } = useWebSocket();
  const store = useChatStore();
  const config = useConfigStore((s) => s.config);
  const loadConfig = useConfigStore((s) => s.loadFromStorage);
  const messagesEnd = useRef<HTMLDivElement>(null);
  const [typingMessageId, setTypingMessageId] = useState<string | null>(null);
  const [showIdleHint, setShowIdleHint] = useState(false);
  const lastUserMsgTime = useRef<number>(Date.now());

  useEffect(() => {
    loadConfig();
    if (!config.apiKey) {
      navigate("/settings");
      return;
    }
  }, []);

  useEffect(() => {
    messagesEnd.current?.scrollIntoView({ behavior: "smooth" });
  }, [store.messages, typingMessageId]);

  useEffect(() => {
    const unsub1 = on("connected", () => {
      store.setConnectionStatus("connected");
      send({
        type: "config",
        provider: config.provider,
        api_key: config.apiKey,
        model: config.model,
        base_url: config.baseUrl,
      });
    });

    const unsub2 = on("disconnected", () => store.setConnectionStatus("disconnected"));
    const unsub3 = on("error", (d) => store.setError(d.error as string));

    const unsub4 = on("reply", (d) => {
      const msgId = `ai_${d.turn}_${Date.now()}`;
      store.addMessage({
        id: msgId,
        role: "assistant",
        content: d.content as string,
        timestamp: Date.now(),
        phase: d.phase as string,
      });
      setTypingMessageId(msgId);
      if (d.session_id) store.setSessionId(d.session_id as string);
      if (d.phase) store.setPhase(d.phase as string, d.phase_label as string);
      if (d.mbti_hint) store.setMbtiHint(d.mbti_hint as string);
      if (d.defense_flags) store.setDefenseFlags(d.defense_flags as string[]);
      if (d.is_final) {
        store.setIsFinal(true);
        if (d.report && d.session_id) {
          setTimeout(() => navigate(`/report/${d.session_id}`), 2000);
        }
      }
    });

    const unsub5 = on("safety_alert", (d) => {
      store.addMessage({
        id: `safety_${Date.now()}`,
        role: "system",
        content: d.content as string,
        timestamp: Date.now(),
      });
    });

    return () => { unsub1(); unsub2(); unsub3(); unsub4(); unsub5(); };
  }, [config]);

  const handleSend = useCallback((text: string) => {
    lastUserMsgTime.current = Date.now();
    setShowIdleHint(false);
    store.addMessage({
      id: `user_${Date.now()}`,
      role: "user",
      content: text,
      timestamp: Date.now(),
    });
    store.setError(null);
    send({
      type: "message",
      content: text,
      session_id: store.sessionId,
      provider: config.provider,
      api_key: config.apiKey,
      model: config.model,
      base_url: config.baseUrl,
    });
  }, [send, store.sessionId, config]);

  const handleIdle = useCallback(() => {
    setShowIdleHint(true);
  }, []);

  const handleActivity = useCallback(() => {
    setShowIdleHint(false);
    lastUserMsgTime.current = Date.now();
  }, []);

  return (
    <div className="flex min-h-screen flex-col bg-cream-50">
      <header className="border-b border-sage-200 bg-cream-50 px-4 py-3">
        <div className="mx-auto flex max-w-2xl items-center justify-between">
          <h1 className="text-lg font-semibold text-sage-800">人格织梦者</h1>
          <div className="flex items-center gap-3">
            {store.mbtiHint && (
              <span className="animate-fade-in rounded-full bg-warm-100 px-3 py-1 text-xs font-medium text-warm-700">
                {store.mbtiHint}
              </span>
            )}
            <span className={`h-2 w-2 rounded-full transition-colors duration-300 ${
              store.connectionStatus === "connected"
                ? "bg-green-500"
                : store.connectionStatus === "connecting"
                  ? "bg-yellow-400 animate-pulse-once"
                  : "bg-red-400"
            }`} />
            <button
              type="button"
              onClick={() => navigate("/settings")}
              className="text-xs text-sage-500 underline"
            >
              设置
            </button>
          </div>
        </div>
      </header>

      <PhaseIndicator phase={store.phase} phaseLabel={store.phaseLabel} />

      {/* Idle reminder */}
      {showIdleHint && (
        <div className="animate-slide-down bg-warm-50 px-4 py-2 text-center">
          <p className="text-sm text-warm-600">
            慢慢来，不用着急。你可以按照自己的节奏思考和表达。
          </p>
        </div>
      )}

      <main className="flex-1 overflow-y-auto px-4 py-4 chat-scroll">
        <div className="mx-auto max-w-2xl">
          {store.messages.length === 0 && (
            <div className="py-20 text-center animate-fade-in">
              <p className="mb-2 text-lg text-sage-600">
                在对话中发现自己
              </p>
              <p className="text-sm text-sage-400">
                开始输入，AI 将通过深度对话了解你的性格
              </p>
            </div>
          )}
          {store.messages.map((m) => (
            <ChatBubble
              key={m.id}
              role={m.role}
              content={m.content}
              timestamp={m.timestamp}
              typing={m.id === typingMessageId && m.role === "assistant"}
            />
          ))}
          {store.error && (
            <div className="mb-4 animate-fade-in rounded-xl bg-red-50 px-4 py-2 text-sm text-red-500">
              {store.error}
            </div>
          )}
          {store.isFinal && (
            <div className="mb-4 animate-fade-in rounded-xl bg-green-50 px-4 py-3 text-center text-sm text-green-700">
              对话已完成，正在跳转至报告页面...
            </div>
          )}
          <div ref={messagesEnd} />
        </div>
      </main>

      <div className="mx-auto w-full max-w-2xl">
        <ChatInput
          onSend={handleSend}
          disabled={store.connectionStatus !== "connected"}
          onIdle={handleIdle}
          onActivity={handleActivity}
        />
      </div>
    </div>
  );
}
