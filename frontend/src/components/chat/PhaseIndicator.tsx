const PHASES = [
  { key: "RAPPORT", label: "建立连接", icon: "1", description: "破冰暖场" },
  { key: "EXPLORATION", label: "深入探索", icon: "2", description: "情境隐喻" },
  { key: "CONFRONTATION", label: "核心对峙", icon: "3", description: "两难困境" },
  { key: "SYNTHESIS", label: "整理画像", icon: "4", description: "镜像校准" },
];

interface Props {
  phase: string;
  phaseLabel: string;
}

export function PhaseIndicator({ phase, phaseLabel }: Props) {
  const currentIdx = PHASES.findIndex((p) => p.key === phase);

  return (
    <div className="border-b border-sage-200 bg-cream-50 px-4 py-2">
      <div className="mx-auto flex max-w-2xl items-center justify-between">
        <div className="flex items-center gap-0.5">
          {PHASES.map((p, i) => (
            <div key={p.key} className="flex items-center">
              {/* Connector line */}
              {i > 0 && (
                <div
                  className={`h-0.5 w-4 transition-colors duration-500 ${
                    i <= currentIdx ? "bg-warm-400" : "bg-sage-200"
                  }`}
                />
              )}
              <div
                className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-medium transition-all duration-500 ${
                  i === currentIdx
                    ? "bg-warm-500 text-white scale-110 shadow-md"
                    : i < currentIdx
                      ? "bg-warm-400 text-white"
                      : "bg-sage-100 text-sage-400"
                }`}
              >
                {p.icon}
              </div>
            </div>
          ))}
        </div>
        <div className="text-right">
          <span className="text-xs font-medium text-sage-600">{phaseLabel}</span>
          {currentIdx >= 0 && (
            <p className="text-[10px] text-sage-400">{PHASES[currentIdx].description}</p>
          )}
        </div>
      </div>
    </div>
  );
}
