import { useEffect, useRef } from "react";
import { chatSocket } from "@/lib/ws";

export function useWebSocket() {
  const cleanupRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    chatSocket.connect();
    return () => {
      // Don't disconnect on unmount — keep alive for SPA navigation
    };
  }, []);

  const on = (type: string, handler: (data: Record<string, unknown>) => void) => {
    const unsub = chatSocket.on(type, handler);
    const prev = cleanupRef.current;
    cleanupRef.current = () => { unsub(); prev?.(); };
    return unsub;
  };

  const send = (data: Record<string, unknown>) => chatSocket.send(data);

  // Cleanup all listeners on unmount
  useEffect(() => {
    return () => { cleanupRef.current?.(); };
  }, []);

  return { send, on, ready: chatSocket.ready };
}
