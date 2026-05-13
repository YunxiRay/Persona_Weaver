import ReactEChartsCore from "echarts-for-react/lib/core";
import * as echarts from "echarts/core";
import { RadarChart } from "echarts/charts";
import {
  GridComponent,
  LegendComponent,
  TitleComponent,
  TooltipComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

echarts.use([RadarChart, GridComponent, LegendComponent, TitleComponent, TooltipComponent, CanvasRenderer]);

interface Props {
  work: { E_I: number; S_N: number; T_F: number; J_P: number };
  relationship: { E_I: number; S_N: number; T_F: number; J_P: number };
  crisis: { E_I: number; S_N: number; T_F: number; J_P: number };
}

// 双极标注，与后端 bayesian.py determine_mbti() 符号约定一致
// E_I: + = 外向(E), - = 内向(I)
// S_N: + = 实感(S), - = 直觉(N)
// T_F: + = 情感(F), - = 思维(T)
// J_P: + = 判断(J), - = 感知(P)
const INDICATORS = [
  { name: "内向 I ⟷ 外向 E", max: 1 },
  { name: "直觉 N ⟷ 实感 S", max: 1 },
  { name: "情感 F ⟷ 思维 T", max: 1 },
  { name: "感知 P ⟷ 判断 J", max: 1 },
];

const DIM_LABELS: Record<string, { left: string; right: string; positive: string; negative: string }> = {
  E_I: { left: "内向 I", right: "外向 E", positive: "E (外向)", negative: "I (内向)" },
  S_N: { left: "直觉 N", right: "实感 S", positive: "S (实感)", negative: "N (直觉)" },
  T_F: { left: "情感 F", right: "思维 T", positive: "F (情感)", negative: "T (思维)" },
  J_P: { left: "感知 P", right: "判断 J", positive: "J (判断)", negative: "P (感知)" },
};

// 使用绝对值展示强度（不论正负方向），让内向/直觉/感知型也有可见的雷达面积
function toSeriesData(dimensions: { E_I: number; S_N: number; T_F: number; J_P: number }): number[] {
  return [
    Math.abs(dimensions.E_I),
    Math.abs(dimensions.S_N),
    Math.abs(dimensions.T_F),
    Math.abs(dimensions.J_P),
  ];
}

// 获取当前偏好的文字标签
function getPreferenceHints(dimensions: { E_I: number; S_N: number; T_F: number; J_P: number }): string[] {
  return (Object.keys(dimensions) as Array<keyof typeof dimensions>).map((key) => {
    const val = dimensions[key];
    const info = DIM_LABELS[key];
    if (Math.abs(val) < 0.1) return info.left + " / " + info.right + " (均衡)";
    return val > 0 ? info.positive : info.negative;
  });
}

function buildOption(label: string, data: number[], color: string) {
  return {
    radar: {
      indicator: INDICATORS,
      center: ["50%", "55%"],
      radius: "65%",
      axisName: { color: "#6B7280", fontSize: 10, borderRadius: 3, padding: [2, 4] },
      splitArea: {
        areaStyle: { color: ["#F7F8F4", "#FFFDF7", "#F7F8F4", "#FFFDF7"] },
      },
      splitLine: { lineStyle: { color: "#DADDCC" } },
      axisLine: { lineStyle: { color: "#C0C4A8" } },
    },
    series: [
      {
        type: "radar",
        name: label,
        data: [{ value: data, name: label }],
        symbol: "circle",
        symbolSize: 5,
        lineStyle: { color, width: 2 },
        itemStyle: { color },
        areaStyle: { color: color + "22" },
      },
    ],
  };
}

export function CognitiveMap({ work, relationship, crisis }: Props) {
  const contexts = [
    { label: "工作情境", data: toSeriesData(work), color: "#C48059", dims: work },
    { label: "情感情境", data: toSeriesData(relationship), color: "#888D66", dims: relationship },
    { label: "危机情境", data: toSeriesData(crisis), color: "#A86542", dims: crisis },
  ];

  return (
    <div className="rounded-2xl border border-sage-200 bg-white p-6">
      <h3 className="mb-2 text-lg font-semibold text-sage-800">认知地图</h3>
      <p className="mb-4 text-xs text-sage-500">
        不同情境下的决策倾向。雷达面积表示特质的强度，标签方向表示当前偏好。
      </p>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {contexts.map((ctx) => {
          const hints = getPreferenceHints(ctx.dims);
          return (
            <div key={ctx.label} className="text-center">
              <ReactEChartsCore
                echarts={echarts}
                option={buildOption(ctx.label, ctx.data, ctx.color)}
                style={{ height: 220 }}
                notMerge
              />
              <p className="text-xs font-medium text-sage-600">{ctx.label}</p>
              <div className="mt-1 text-[10px] leading-relaxed text-sage-400">
                {hints.map((hint, i) => (
                  <span key={i} className="mx-1 inline-block">{hint}</span>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
