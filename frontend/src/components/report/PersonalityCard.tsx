interface DimBarProps {
  label: string;
  left: string;
  right: string;
  score: number;  // -1 to 1
  confidence: number;
}

function DimBar({ label, left, right, score, confidence }: DimBarProps) {
  const pct = ((score + 1) / 2) * 100;
  return (
    <div className="mb-3">
      <div className="mb-1 flex justify-between text-xs text-sage-500">
        <span>{left}</span>
        <span>{label} ({Math.round(confidence * 100)}%)</span>
        <span>{right}</span>
      </div>
      <div className="h-3 overflow-hidden rounded-full bg-sage-100">
        <div
          className="h-full rounded-full bg-gradient-to-r from-warm-300 to-warm-500 transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

interface Props {
  mbtiType: string;
  dimensions: { E_I: number; S_N: number; T_F: number; J_P: number };
  confidence: { E_I: number; S_N: number; T_F: number; J_P: number };
}

export function PersonalityCard({ mbtiType, dimensions, confidence }: Props) {
  return (
    <div className="rounded-2xl border border-sage-200 bg-white p-6">
      <div className="mb-4 text-center">
        <span className="text-3xl font-bold tracking-widest text-warm-600">{mbtiType}</span>
      </div>
      <DimBar label="能量来源" left="内向 (I)" right="外向 (E)" score={dimensions.E_I} confidence={confidence.E_I} />
      <DimBar label="信息获取" left="直觉 (N)" right="实感 (S)" score={dimensions.S_N} confidence={confidence.S_N} />
      <DimBar label="决策方式" left="思维 (T)" right="情感 (F)" score={dimensions.T_F} confidence={confidence.T_F} />
      <DimBar label="生活方式" left="感知 (P)" right="判断 (J)" score={dimensions.J_P} confidence={confidence.J_P} />
    </div>
  );
}
