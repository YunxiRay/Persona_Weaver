import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4">
      <main className="flex max-w-lg flex-col items-center text-center">
        <h1 className="mb-4 text-4xl font-bold tracking-tight text-sage-800">
          人格织梦者
        </h1>
        <p className="mb-2 text-lg text-sage-600">Persona Weaver</p>
        <p className="mb-8 text-sage-500">在对话中发现自己</p>

        <p className="mb-8 leading-relaxed text-sage-600">
          通过一场四阶段的深度对话，AI
          将模拟真实的心理咨询体验，在自然叙事中还原你最真实的人格底色。这不是问卷，而是一次自我探索之旅。
        </p>

        <Link
          to="/chat"
          className="rounded-2xl bg-warm-500 px-8 py-3 text-lg font-medium text-white shadow-sm transition-colors hover:bg-warm-600"
        >
          开始对话
        </Link>

        <p className="mt-12 text-sm text-sage-400">
          本工具提供的报告仅为心理类型倾向参考，不能替代专业心理诊断或治疗。
          <br />
          用户需年满 16 周岁。
        </p>
      </main>
    </div>
  );
}
