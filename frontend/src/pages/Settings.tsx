import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ApiKeyInput } from "@/components/settings/ApiKeyInput";
import { ConnectionTest } from "@/components/settings/ConnectionTest";
import { ProviderSelector } from "@/components/settings/ProviderSelector";
import { useConfigStore } from "@/stores/configStore";

export const PROVIDERS = [
  { value: "deepseek", label: "DeepSeek", model: "deepseek-chat", link: "https://platform.deepseek.com" },
  { value: "qwen", label: "通义千问", model: "qwen-plus", link: "https://dashscope.aliyun.com" },
  { value: "glm", label: "智谱 GLM", model: "glm-4", link: "https://open.bigmodel.cn" },
  { value: "moonshot", label: "Moonshot (Kimi)", model: "moonshot-v1-8k", link: "https://platform.moonshot.cn" },
  { value: "openai_compatible", label: "OpenAI 兼容", model: "自定义", link: "" },
];

const PROVIDER_DEFAULTS: Record<string, string> = {
  deepseek: "https://api.deepseek.com/v1",
  qwen: "https://dashscope.aliyuncs.com/compatible-mode/v1",
  glm: "https://open.bigmodel.cn/api/paas/v4",
  moonshot: "https://api.moonshot.cn/v1",
};

export default function Settings() {
  const navigate = useNavigate();
  const { config, setConfig, loadFromStorage } = useConfigStore();
  const [showAdvanced, setShowAdvanced] = useState(false);

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

  return (
    <div className="flex min-h-screen flex-col items-center bg-cream-50 px-4 py-12">
      <div className="w-full max-w-lg">
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
        </div>
      </div>
    </div>
  );
}
