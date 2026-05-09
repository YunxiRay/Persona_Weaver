import { Link } from "react-router-dom";

export default function Terms() {
  return (
    <div className="min-h-screen bg-cream-50 px-4 py-12">
      <div className="mx-auto max-w-2xl">
        <Link to="/" className="mb-6 inline-block text-sm text-sage-500 underline">
          &larr; 返回首页
        </Link>
        <h1 className="mb-6 text-2xl font-bold text-sage-800">用户协议</h1>
        <div className="space-y-4 text-sm leading-relaxed text-sage-700">
          <p>最后更新：2026 年 5 月</p>

          <section>
            <h2 className="mb-2 text-base font-semibold text-sage-800">1. 服务说明</h2>
            <p>
              人格织梦者（Persona Weaver）是一款基于深度对话的 MBTI 心理类型倾向分析工具。
              本工具通过多轮递进式对话和贝叶斯推理引擎，为用户提供性格倾向参考报告。
              本工具<strong>不构成医疗诊断、心理咨询或治疗服务</strong>。
            </p>
          </section>

          <section>
            <h2 className="mb-2 text-base font-semibold text-sage-800">2. 年龄要求</h2>
            <p>用户须年满 16 周岁方可使用本工具。16-18 周岁的未成年用户建议在监护人陪同下使用。</p>
          </section>

          <section>
            <h2 className="mb-2 text-base font-semibold text-sage-800">3. 用户责任</h2>
            <ul className="list-inside list-disc space-y-1 text-sage-600">
              <li>用户需自行配置 AI 厂商的 API Key，并对 API 调用的费用负责</li>
              <li>用户应保证输入内容的合法性，不得利用本工具生成违法或有害内容</li>
              <li>用户应理解 AI 生成内容的局限性，报告的解读仅供参考</li>
            </ul>
          </section>

          <section>
            <h2 className="mb-2 text-base font-semibold text-sage-800">4. 免责声明</h2>
            <ul className="list-inside list-disc space-y-1 text-sage-600">
              <li>本工具报告仅为心理类型"倾向参考"，展示置信度区间而非绝对判断</li>
              <li>MBTI 框架在心理学领域存在科学争议，请理性看待分析结果</li>
              <li>如果你正在经历心理困扰或危机，请立即拨打心理援助热线（12320）或寻求专业帮助</li>
              <li>项目维护者对因使用本工具而产生的任何直接或间接损失不承担责任</li>
            </ul>
          </section>

          <section>
            <h2 className="mb-2 text-base font-semibold text-sage-800">5. 开源许可</h2>
            <p>
              人格织梦者基于 MIT License 开源。你可以自由使用、修改和分发本项目代码，
              但需保留原始版权声明和许可说明。
            </p>
          </section>

          <section>
            <h2 className="mb-2 text-base font-semibold text-sage-800">6. 协议变更</h2>
            <p>
              我们可能不时更新本协议。重大变更将在项目主页或应用中显著位置通知。
              继续使用本工具即表示你同意更新后的条款。
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
