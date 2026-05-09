import { useState } from "react";
import { api } from "@/lib/api";

interface Props {
  provider: string;
  apiKey: string;
  model: string;
  baseUrl: string;
}

type Status = "idle" | "testing" | "success" | "failed";

export function ConnectionTest({ provider, apiKey, model, baseUrl }: Props) {
  const [status, setStatus] = useState<Status>("idle");
  const [message, setMessage] = useState("");

  const test = async () => {
    if (!apiKey) return;
    setStatus("testing");
    setMessage("");
    try {
      const res = await api.post<{ success: boolean; error?: string }>("/config/llm/test", {
        provider,
        api_key: apiKey,
        model: model || undefined,
        base_url: baseUrl || undefined,
      });
      if (res.success) {
        setStatus("success");
        setMessage("连接成功");
      } else {
        setStatus("failed");
        setMessage(res.error || "连接失败");
      }
    } catch (e) {
      setStatus("failed");
      setMessage(e instanceof Error ? e.message : "网络错误");
    }
  };

  return (
    <div>
      <button
        type="button"
        onClick={test}
        disabled={status === "testing" || !apiKey}
        className="rounded-xl bg-warm-500 px-6 py-2.5 text-sm font-medium text-white transition-colors hover:bg-warm-600 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {status === "testing" ? "测试中..." : "测试连接"}
      </button>
      {message && (
        <span
          className={`ml-3 text-sm ${
            status === "success" ? "text-green-600" : "text-red-500"
          }`}
        >
          {message}
        </span>
      )}
    </div>
  );
}
