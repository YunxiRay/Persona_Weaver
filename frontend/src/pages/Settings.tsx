import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ApiKeyInput } from "@/components/settings/ApiKeyInput";
import { ConnectionTest } from "@/components/settings/ConnectionTest";
import { ProviderSelector } from "@/components/settings/ProviderSelector";
import { useConfigStore } from "@/stores/configStore";
import { api } from "@/lib/api";

export const PROVIDERS = [
  { value: "deepseek", label: "DeepSeek", model: "deepseek-v4-flash", link: "https://platform.deepseek.com" },
  { value: "qwen", label: "通义千问", model: "qwen3.6-plus", link: "https://dashscope.aliyun.com" },
  { value: "glm", label: "智谱 GLM", model: "GLM-4.7", link: "https://open.bigmodel.cn" },
  { value: "moonshot", label: "Kimi (Moonshot)", model: "kimi-k2-turbo-preview", link: "https://platform.kimi.com" },
  { value: "openai_compatible", label: "OpenAI 兼容", model: "自定义", link: "" },
];

const PROVIDER_DEFAULTS: Record<string, string> = {
  deepseek: "https://api.deepseek.com",
  qwen: "https://dashscope.aliyuncs.com/compatible-mode/v1",
  glm: "https://open.bigmodel.cn/api/paas/v4",
  moonshot: "https://api.moonshot.cn/v1",
};

export default function Settings() {
  const navigate = useNavigate();
  const { config, setConfig, loadFromStorage } = useConfigStore();
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [cleared, setCleared] = useState(false);

  useEffect(() => {
    loadFromStorage();
  }, []);

  const handleProviderChange = (provider: string) => {
    const defaults = PROVIDERS.find((p) => p.value === provider);
    setConfig({
      provider,
      model: defaults?.model || "",
      baseUrl: PROVIDER_DEFAULTS[provider] || "",
    });
  };

  const handleClearData = async () => {
    setClearing(true);
    try {
      await api.del("/data");
      setConfig({ apiKey: "" });
      setCleared(true);
      setShowClearConfirm(false);
      setTimeout(() => {
        navigate("/");
      }, 2000);
    } catch {
      setClearing(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center bg-cream-50 px-4 py-12">
      <div className="w-full max-w-lg">
        {/* Onboarding banner for first-time users */}
        {!config.apiKey && (
          <div className="mb-6 rounded-xl border border-warm-300 bg-warm-50 px-5 py-4">
            <p className="text-sm font-medium text-warm-700">
              欢迎使用人格织梦者！请先配置 LLM 接口
            </p>
            <p className="mt-1 text-xs text-warm-500">
              本项目不内置 API Key，你需要从以下厂商获取 Key 后填入下方。配置完成后可测试连接。
            </p>
            <p className="mt-1 text-xs text-warm-600">
              ⚠️ 建议使用一个全新的 API Key，避免在其他 AI 应用中的聊天记录被当作上下文影响对话质量。
            </p>
          </div>
        )}

        <h1 className="mb-2 text-2xl font-bold text-sage-800">LLM 配置</h1>
        <p className="mb-8 text-sage-500">
          选择你使用的 AI 厂商并填入 API Key。Key 仅保存在你的浏览器中，不会上传到服务器。
        </p>

        <div className="space-y-6">
          {/* Provider Selector */}
          <div>
            <label className="mb-2 block text-sm font-medium text-sage-700">AI 厂商</label>
            <ProviderSelector selected={config.provider} onChange={handleProviderChange} />
          </div>

          {/* API Key */}
          <ApiKeyInput
            value={config.apiKey}
            onChange={(v) => setConfig({ apiKey: v })}
          />

          {/* Model */}
          <div>
            <label className="mb-1 block text-sm font-medium text-sage-700">模型</label>
            <input
              type="text"
              value={config.model}
              onChange={(e) => setConfig({ model: e.target.value })}
              className="w-full rounded-xl border border-sage-200 px-4 py-2.5 text-sage-800 focus:border-warm-400 focus:outline-none"
            />
          </div>

          {/* Advanced: Base URL */}
          <div>
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="text-sm text-sage-500 underline"
            >
              {showAdvanced ? "收起高级选项" : "高级选项"}
            </button>
            {showAdvanced && (
              <div className="mt-2">
                <label className="mb-1 block text-sm font-medium text-sage-700">Base URL</label>
                <input
                  type="text"
                  value={config.baseUrl}
                  onChange={(e) => setConfig({ baseUrl: e.target.value })}
                  placeholder={PROVIDER_DEFAULTS[config.provider] || ""}
                  className="w-full rounded-xl border border-sage-200 px-4 py-2.5 text-sage-800 placeholder-sage-300 focus:border-warm-400 focus:outline-none"
                />
              </div>
            )}
          </div>

          {/* Test Connection */}
          <ConnectionTest
            provider={config.provider}
            apiKey={config.apiKey}
            model={config.model}
            baseUrl={config.baseUrl}
          />

          {/* Status */}
          <div className="rounded-xl bg-sage-100 px-4 py-3">
            <span className="text-sm text-sage-600">
              状态：{config.apiKey ? "已配置" : "未配置"}
            </span>
          </div>

          {/* Back */}
          <button
            type="button"
            onClick={() => navigate("/")}
            className="w-full rounded-xl border border-sage-300 py-2.5 text-sm text-sage-600 transition-colors hover:bg-sage-50"
          >
            返回首页
          </button>

          {/* Start Chat button (when configured) */}
          {config.apiKey && (
            <button
              type="button"
              onClick={() => navigate("/chat")}
              className="w-full rounded-xl bg-warm-500 py-3 text-base font-medium text-white shadow-sm transition-all hover:bg-warm-600 hover:shadow-md active:scale-[0.98]"
            >
              开始人格分析
            </button>
          )}

          {/* 清除历史记录 */}
          <div className="border-t border-sage-200 pt-6">
            {cleared ? (
              <div className="rounded-xl bg-sage-100 px-4 py-3 text-center text-sm text-sage-700">
                历史记录已清除，即将返回首页...
              </div>
            ) : showClearConfirm ? (
              <div className="rounded-xl border-2 border-red-200 bg-red-50 px-4 py-4">
                <p className="mb-3 text-sm text-red-700">
                  此操作将清除所有对话记录、分析报告和配置信息，不可恢复。确定继续？
                </p>
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={handleClearData}
                    disabled={clearing}
                    className="flex-1 rounded-lg bg-red-500 py-2 text-sm text-white transition-colors hover:bg-red-600 disabled:opacity-50"
                  >
                    {clearing ? "清除中..." : "确定清除"}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowClearConfirm(false)}
                    className="flex-1 rounded-lg border border-sage-300 py-2 text-sm text-sage-600 transition-colors hover:bg-sage-50"
                  >
                    取消
                  </button>
                </div>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => setShowClearConfirm(true)}
                className="w-full rounded-xl border border-red-300 py-2.5 text-sm text-red-500 transition-colors hover:bg-red-50"
              >
                清除所有历史记录
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
