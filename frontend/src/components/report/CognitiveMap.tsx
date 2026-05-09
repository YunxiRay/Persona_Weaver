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

const INDICATORS = [
  { name: "外向 E", max: 1 },
  { name: "实感 S", max: 1 },
  { name: "思维 T", max: 1 },
  { name: "判断 J", max: 1 },
];

function toSeriesData(dimensions: { E_I: number; S_N: number; T_F: number; J_P: number }): number[] {
  return [
    Math.max(0, dimensions.E_I), // E_I: -1~1 E-leaning, map to 0~1
    Math.max(0, dimensions.S_N), // S_N: -1~1 S-leaning
    Math.max(0, dimensions.T_F), // T_F: -1~1 T-leaning
    Math.max(0, dimensions.J_P), // J_P: -1~1 J-leaning
  ];
}

function buildOption(label: string, data: number[], color: string) {
  return {
    radar: {
      indicator: INDICATORS,
      center: ["50%", "55%"],
      radius: "65%",
      axisName: { color: "#6B7280", fontSize: 11, borderRadius: 3, padding: [2, 4] },
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
    { label: "工作情境", data: toSeriesData(work), color: "#C48059" },
    { label: "情感情境", data: toSeriesData(relationship), color: "#888D66" },
    { label: "危机情境", data: toSeriesData(crisis), color: "#A86542" },
  ];

  return (
    <div className="rounded-2xl border border-sage-200 bg-white p-6">
      <h3 className="mb-2 text-lg font-semibold text-sage-800">认知地图</h3>
      <p className="mb-4 text-xs text-sage-500">
        不同情境下的决策倾向。每个雷达图分别展示工作、情感和危机情境下的维度分布。
      </p>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {contexts.map((ctx) => (
          <div key={ctx.label} className="text-center">
            <ReactEChartsCore
              echarts={echarts}
              option={buildOption(ctx.label, ctx.data, ctx.color)}
              style={{ height: 220 }}
              notMerge
            />
            <p className="text-xs font-medium text-sage-600">{ctx.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
