import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useConfigStore } from "@/stores/configStore";

function AgeModal({ onConfirm }: { onConfirm: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="mx-4 w-full max-w-sm rounded-2xl bg-white p-6 shadow-xl">
        <h2 className="mb-2 text-lg font-semibold text-sage-800">年龄确认</h2>
        <p className="mb-4 text-sm text-sage-600">
          人格织梦者是一款基于深度对话的心理类型倾向分析工具。根据相关法律与伦理要求，用户需年满 16 周岁方可使用。
        </p>
        <div className="flex gap-3">
          <a
            href="https://www.12320.gov.cn"
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 rounded-xl border border-sage-300 py-2.5 text-center text-sm text-sage-600"
          >
            了解更多
          </a>
          <button
            onClick={onConfirm}
            className="flex-1 rounded-xl bg-warm-500 py-2.5 text-sm font-medium text-white"
          >
            我已满 16 岁
          </button>
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  const navigate = useNavigate();
  const { config, loadFromStorage } = useConfigStore();
  const [showAgeModal, setShowAgeModal] = useState(false);

  useEffect(() => {
    loadFromStorage();
  }, []);

  const handleStart = () => {
    if (!localStorage.getItem("pw_age_confirmed")) {
      setShowAgeModal(true);
    } else if (config.apiKey) {
      navigate("/chat");
    } else {
      navigate("/settings");
    }
  };

  const handleAgeConfirm = () => {
    localStorage.setItem("pw_age_confirmed", "true");
    setShowAgeModal(false);
    if (config.apiKey) {
      navigate("/chat");
    } else {
      navigate("/settings");
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-cream-50 px-4">
      {showAgeModal && <AgeModal onConfirm={handleAgeConfirm} />}

      <main className="flex max-w-lg flex-col items-center text-center">
        <div className="stagger-item">
          <h1 className="mb-3 text-4xl font-bold tracking-tight text-sage-800 sm:text-5xl">
            人格织梦者
          </h1>
          <p className="mb-1 text-lg text-sage-600">Persona Weaver</p>
          <p className="mb-8 text-sage-500">在对话中发现自己</p>
        </div>

        <p className="stagger-item mb-8 leading-relaxed text-sage-600">
          通过一场四阶段的深度对话，AI
          将模拟真实的心理咨询体验。在你不自知的情况下，通过跨情境隐喻和两难困境，采集最真实的人格语料。
          <strong>这不是问卷，而是一次自我探索之旅。</strong>
        </p>

        <div className="stagger-item">
          <button
            onClick={handleStart}
            className="mb-3 rounded-2xl bg-warm-500 px-10 py-3.5 text-lg font-medium text-white shadow-sm transition-all hover:bg-warm-600 hover:shadow-md active:scale-95"
          >
            开始对话
          </button>
        </div>

        {config.apiKey ? (
          <Link to="/settings" className="stagger-item text-sm text-sage-500 underline transition-colors hover:text-sage-700">
            LLM 设置
          </Link>
        ) : (
          <p className="stagger-item text-sm text-sage-400">
            首次使用？请先配置你的 AI 厂商 API Key
          </p>
        )}

        {/* Features */}
        <div className="mt-12 grid w-full grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="stagger-item rounded-xl border border-sage-200 bg-white p-4 transition-shadow hover:shadow-md">
            <div className="mb-2 text-2xl">1</div>
            <h3 className="mb-1 font-semibold text-sage-800">四阶段对话</h3>
            <p className="text-xs text-sage-500">破冰 → 探索 → 对峙 → 收束，模拟专业心理咨询节奏</p>
          </div>
          <div className="stagger-item rounded-xl border border-sage-200 bg-white p-4 transition-shadow hover:shadow-md">
            <div className="mb-2 text-2xl">2</div>
            <h3 className="mb-1 font-semibold text-sage-800">贝叶斯推理</h3>
            <p className="text-xs text-sage-500">随语料累积实时更新人格维度置信度，而非一次性打分</p>
          </div>
          <div className="stagger-item rounded-xl border border-sage-200 bg-white p-4 transition-shadow hover:shadow-md">
            <div className="mb-2 text-2xl">3</div>
            <h3 className="mb-1 font-semibold text-sage-800">深度报告</h3>
            <p className="text-xs text-sage-500">性格骨架 / 认知地图 / 语言素描 / 趣味标签 / 心理寄语</p>
          </div>
        </div>

        {/* Ethical disclaimer */}
        <div className="stagger-item mt-12 rounded-xl bg-sage-100 px-6 py-4 text-center">
          <p className="text-sm font-semibold text-sage-700">非医疗诊断声明</p>
          <p className="mt-1 text-xs text-sage-500">
            本工具提供的报告仅为心理类型倾向参考，不能替代专业心理诊断或治疗。
            <br />
            用户需年满 16 周岁。对话数据默认匿名存储，仅用于当次分析，用户可随时清除。
          </p>
          <p className="mt-2 text-xs text-sage-400">
            心理援助热线：12320（24小时）| 全国心理援助热线：400-161-9995
          </p>
        </div>
      </main>

      <footer className="mt-12 pb-6 text-center text-xs text-sage-400">
        <p>Persona Weaver &copy; 2026 | MIT License | 仅简体中文</p>
        <div className="mt-2 flex justify-center gap-4">
          <Link to="/privacy" className="underline transition-colors hover:text-sage-600">隐私政策</Link>
          <Link to="/terms" className="underline transition-colors hover:text-sage-600">用户协议</Link>
        </div>
      </footer>
    </div>
  );
}
