import { Link } from "react-router-dom";

export default function Privacy() {
  return (
    <div className="min-h-screen bg-cream-50 px-4 py-12">
      <div className="mx-auto max-w-2xl">
        <Link to="/" className="mb-6 inline-block text-sm text-sage-500 underline">
          &larr; 返回首页
        </Link>
        <h1 className="mb-6 text-2xl font-bold text-sage-800">隐私政策</h1>
        <div className="space-y-4 text-sm leading-relaxed text-sage-700">
          <p>最后更新：2026 年 5 月</p>

          <section>
            <h2 className="mb-2 text-base font-semibold text-sage-800">1. 信息收集</h2>
            <p>人格织梦者（Persona Weaver）是一款开源的 MBTI 倾向分析工具。我们遵循"数据最小化"原则：</p>
            <ul className="mt-1 list-inside list-disc space-y-1 text-sage-600">
              <li>对话内容仅用于当次人格分析，默认为匿名模式，无需注册账号</li>
              <li>你的 API Key 仅保存在浏览器本地存储（localStorage），不会上传至服务器</li>
              <li>对话过程中采集的语言特征和维度快照仅关联一个随机生成的会话 ID</li>
            </ul>
          </section>

          <section>
            <h2 className="mb-2 text-base font-semibold text-sage-800">2. 数据存储与保留</h2>
            <ul className="list-inside list-disc space-y-1 text-sage-600">
              <li>匿名会话数据默认保留 7 天，到期后自动清除</li>
              <li>对话消息、维度快照和生成的报告在保留期内加密存储于服务器数据库中</li>
              <li>你可以随时通过清除浏览器缓存或结束对话来移除会话数据</li>
            </ul>
          </section>

          <section>
            <h2 className="mb-2 text-base font-semibold text-sage-800">3. 数据安全</h2>
            <ul className="list-inside list-disc space-y-1 text-sage-600">
              <li>所有 API 通信通过 HTTPS/TLS 加密传输</li>
              <li>用户输入经过 XSS/SQL 注入过滤处理</li>
              <li>包含危机关键词（如自伤/自杀相关表述）的输入会触发安全熔断机制，向用户提供心理援助热线信息</li>
            </ul>
          </section>

          <section>
            <h2 className="mb-2 text-base font-semibold text-sage-800">4. 第三方服务</h2>
            <p>你的对话内容会发送给你自行配置的 AI 厂商（如 DeepSeek、通义千问等）的 API 进行处理。请同时参阅你所选择厂商的隐私政策。</p>
          </section>

          <section>
            <h2 className="mb-2 text-base font-semibold text-sage-800">5. 你的权利</h2>
            <ul className="list-inside list-disc space-y-1 text-sage-600">
              <li>有权随时结束对话并清除数据</li>
              <li>有权要求删除与匿名会话关联的所有数据</li>
              <li>本工具不会将数据用于任何商业目的或出售给第三方</li>
            </ul>
          </section>

          <section>
            <h2 className="mb-2 text-base font-semibold text-sage-800">6. 联系我们</h2>
            <p>如有隐私相关问题，请通过 GitHub Issues 联系项目维护者。</p>
          </section>
        </div>
      </div>
    </div>
  );
}
