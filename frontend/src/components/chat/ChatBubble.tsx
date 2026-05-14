import { useEffect, useState, useRef } from "react";
import type { PatternRef } from "@/stores/chatStore";

interface Props {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: number;
  typing?: boolean;
  patternReferences?: PatternRef[];
}

const TYPING_SPEED = 35; // ms per character base
const TYPING_VARIANCE = 15; // random variance for natural feel

export function ChatBubble({ role, content, timestamp, typing, patternReferences }: Props) {
  const isUser = role === "user";
  const isSystem = role === "system";
  const [displayedText, setDisplayedText] = useState(typing ? "" : content);
  const [isTyping, setIsTyping] = useState(typing ?? false);
  const charIndexRef = useRef(0);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const contentRef = useRef(content);

  useEffect(() => {
    contentRef.current = content;

    if (!typing) {
      setDisplayedText(content);
      setIsTyping(false);
      charIndexRef.current = content.length;
      return;
    }

    setIsTyping(true);
    setDisplayedText("");
    charIndexRef.current = 0;

    const typeNext = () => {
      charIndexRef.current += 1;
      const idx = charIndexRef.current;
      setDisplayedText(contentRef.current.slice(0, idx));

      if (idx < contentRef.current.length) {
        const delay = TYPING_SPEED + (Math.random() - 0.5) * 2 * TYPING_VARIANCE;
        timerRef.current = setTimeout(typeNext, Math.max(10, delay));
      } else {
        setIsTyping(false);
      }
    };

    typeNext();

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [content, typing]);

  const bubbleStyle = isUser
    ? "animate-fade-in-up bg-warm-500 text-white"
    : isSystem
      ? "animate-fade-in bg-red-50 border border-red-200 text-red-700"
      : "animate-fade-in-up bg-white border border-sage-200 text-sage-800";

  const bubbleContent = (
    <div className={`max-w-[75%] rounded-2xl px-4 py-3 ${bubbleStyle}`}>
      <p className={`whitespace-pre-wrap text-sm leading-relaxed ${isTyping ? "typing-cursor" : ""}`}>
        {displayedText}
      </p>
      {!isTyping && patternReferences && patternReferences.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1.5">
          {patternReferences.map((ref) => (
            <span
              key={ref.id}
              className="inline-flex items-center rounded-full bg-sage-100 px-2.5 py-0.5 text-xs text-sage-700"
              title={`${ref.category} — 匹配度: ${(ref.score * 100).toFixed(0)}%`}
            >
              {ref.name}
            </span>
          ))}
        </div>
      )}
      {!isTyping && (
        <span className="mt-1 block text-right text-xs opacity-60">
          {new Date(timestamp).toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" })}
        </span>
      )}
    </div>
  );

  if (isSystem) {
    return (
      <div className="mb-3 flex justify-center">
        {bubbleContent}
      </div>
    );
  }

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      {!isUser && (
        <div className="mr-3 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-warm-200 text-xs font-medium text-warm-700">
          PW
        </div>
      )}
      {bubbleContent}
      {isUser && (
        <div className="ml-3 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-sage-200 text-xs font-medium text-sage-600">
          U
        </div>
      )}
    </div>
  );
}
