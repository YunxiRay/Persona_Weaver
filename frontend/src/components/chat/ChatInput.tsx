import { useState, useRef, useEffect, useCallback } from "react";

interface Props {
  onSend: (text: string) => void;
  disabled?: boolean;
  onIdle?: () => void;
  onActivity?: () => void;
}

const IDLE_THRESHOLD_MS = 60_000; // Show gentle reminder after 60s of inactivity

export function ChatInput({ onSend, disabled, onIdle, onActivity }: Props) {
  const [text, setText] = useState("");
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const idleTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const resetIdleTimer = useCallback(() => {
    if (idleTimerRef.current) clearTimeout(idleTimerRef.current);
    onActivity?.();
    idleTimerRef.current = setTimeout(() => onIdle?.(), IDLE_THRESHOLD_MS);
  }, [onIdle, onActivity]);

  useEffect(() => {
    resetIdleTimer();
    return () => { if (idleTimerRef.current) clearTimeout(idleTimerRef.current); };
  }, [resetIdleTimer]);

  const handleSend = () => {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText("");
    resetIdleTimer();
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex items-end gap-2 border-t border-sage-200 bg-cream-50 px-4 py-3">
      <textarea
        ref={inputRef}
        value={text}
        onChange={(e) => { setText(e.target.value); resetIdleTimer(); }}
        onKeyDown={(e) => { handleKeyDown(e); resetIdleTimer(); }}
        placeholder="输入你的想法..."
        rows={2}
        disabled={disabled}
        className="flex-1 resize-none rounded-xl border border-sage-200 bg-white px-4 py-2.5 text-sm text-sage-800 placeholder-sage-300 focus:border-warm-400 focus:outline-none disabled:bg-sage-100"
      />
      <button
        type="button"
        onClick={handleSend}
        disabled={disabled || !text.trim()}
        className="rounded-xl bg-warm-500 px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-warm-600 disabled:cursor-not-allowed disabled:opacity-50"
      >
        发送
      </button>
    </div>
  );
}
