const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws/chat";

type MessageHandler = (data: Record<string, unknown>) => void;

class ChatSocket {
  private ws: WebSocket | null = null;
  private handlers: Map<string, Set<MessageHandler>> = new Map();
  private reconnectAttempts = 0;
  private maxReconnect = 10;
  private reconnectDelay = 1000;
  private pingInterval: number | null = null;

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) return;
    this.ws = new WebSocket(WS_URL);

    this.ws.onopen = () => {
      this.reconnectAttempts = 0;
      this._startPing();
      this._emit("connected", {});
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const type = data.type || "message";
        this._emit(type, data);
        this._emit("*", data);
      } catch {
        // ignore malformed
      }
    };

    this.ws.onclose = () => {
      this._stopPing();
      this._emit("disconnected", {});
      this._tryReconnect();
    };

    this.ws.onerror = () => {
      this._emit("error", { message: "WebSocket 连接错误" });
    };
  }

  send(data: Record<string, unknown>) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  on(type: string, handler: MessageHandler) {
    if (!this.handlers.has(type)) this.handlers.set(type, new Set());
    this.handlers.get(type)!.add(handler);
    return () => this.handlers.get(type)?.delete(handler);
  }

  disconnect() {
    this._stopPing();
    this.ws?.close();
    this.ws = null;
  }

  get ready() { return this.ws?.readyState === WebSocket.OPEN; }

  private _emit(type: string, data: Record<string, unknown>) {
    this.handlers.get(type)?.forEach((h) => h(data));
  }

  private _startPing() {
    this._stopPing();
    this.pingInterval = window.setInterval(() => this.send({ type: "ping" }), 30000);
  }

  private _stopPing() {
    if (this.pingInterval) { clearInterval(this.pingInterval); this.pingInterval = null; }
  }

  private _tryReconnect() {
    if (this.reconnectAttempts >= this.maxReconnect) return;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts);
    this.reconnectAttempts++;
    setTimeout(() => this.connect(), delay);
  }
}

export const chatSocket = new ChatSocket();
