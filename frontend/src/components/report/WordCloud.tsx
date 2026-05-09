interface Props {
  keywords: string[];
  styleLabel: string;
  abstractRatio: number;
  concreteRatio: number;
}

const SIZE_CLASSES = [
  "text-xs", "text-sm", "text-base", "text-lg",
  "text-xl", "text-2xl", "text-3xl", "text-4xl",
];

const COLOR_CLASSES = [
  "text-warm-500", "text-sage-600", "text-warm-600", "text-sage-500",
  "text-warm-400", "text-sage-700", "text-warm-700", "text-sage-400",
  "text-warm-300", "text-sage-800",
];

const WEIGHTS = [
  "font-light", "font-normal", "font-medium", "font-semibold", "font-bold", "font-extrabold",
];

function hashWord(s: string): number {
  let h = 0;
  for (let i = 0; i < s.length; i++) h = (31 * h + s.charCodeAt(i)) | 0;
  return Math.abs(h);
}

export function WordCloud({ keywords, styleLabel, abstractRatio, concreteRatio }: Props) {
  if (keywords.length === 0) {
    return (
      <div className="rounded-2xl border border-sage-200 bg-white p-6">
        <h3 className="mb-2 text-lg font-semibold text-sage-800">语言素描</h3>
        <p className="text-sm text-sage-400">语料不足，无法生成语言素描</p>
      </div>
    );
  }

  const rows: string[][] = [];
  let row: string[] = [];
  let rowLen = 0;
  keywords.slice(0, 20).forEach((w) => {
    if (rowLen + w.length > 18 && row.length > 0) {
      rows.push(row);
      row = [];
      rowLen = 0;
    }
    row.push(w);
    rowLen += w.length;
  });
  if (row.length > 0) rows.push(row);

  return (
    <div className="rounded-2xl border border-sage-200 bg-white p-6">
      <h3 className="mb-1 text-lg font-semibold text-sage-800">语言素描</h3>
      <p className="mb-4 text-sm text-sage-500">{styleLabel}</p>

      {/* Pseudo word-cloud */}
      <div className="mb-6 flex flex-wrap items-center justify-center gap-x-3 gap-y-1 py-4">
        {keywords.slice(0, 20).map((w) => {
          const h = hashWord(w);
          const sizeIdx = h % SIZE_CLASSES.length;
          const colIdx = h % COLOR_CLASSES.length;
          const wIdx = h % WEIGHTS.length;
          return (
            <span
              key={w}
              className={`${SIZE_CLASSES[sizeIdx]} ${COLOR_CLASSES[colIdx]} ${WEIGHTS[wIdx]} inline-block cursor-default transition-transform hover:scale-110`}
            >
              {w}
            </span>
          );
        })}
      </div>

      {/* Ratio bars */}
      <div className="space-y-2">
        <div>
          <div className="flex justify-between text-xs text-sage-500 mb-1">
            <span>抽象词</span>
            <span>{Math.round(abstractRatio * 100)}%</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-sage-100">
            <div
              className="h-full rounded-full bg-gradient-to-r from-sage-400 to-sage-500 transition-all duration-700"
              style={{ width: `${Math.round(abstractRatio * 100)}%` }}
            />
          </div>
        </div>
        <div>
          <div className="flex justify-between text-xs text-sage-500 mb-1">
            <span>具象词</span>
            <span>{Math.round(concreteRatio * 100)}%</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-sage-100">
            <div
              className="h-full rounded-full bg-gradient-to-r from-warm-300 to-warm-400 transition-all duration-700"
              style={{ width: `${Math.round(concreteRatio * 100)}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
