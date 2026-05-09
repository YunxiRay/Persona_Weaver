interface Props {
  note: string;
  socialGuide: string;
  soulMatch: string;
}

export function TherapistNote({ note, socialGuide, soulMatch }: Props) {
  return (
    <div className="space-y-4">
      <div className="rounded-2xl border border-sage-200 bg-white p-6">
        <h3 className="mb-3 text-lg font-semibold text-sage-800">心理医生寄语</h3>
        <p className="leading-relaxed text-sage-700">{note}</p>
      </div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="rounded-2xl border border-sage-200 bg-white p-4">
          <h4 className="mb-1 text-sm font-semibold text-sage-800">社交生存指南</h4>
          <p className="text-sm text-sage-600">{socialGuide}</p>
        </div>
        <div className="rounded-2xl border border-sage-200 bg-white p-4">
          <h4 className="mb-1 text-sm font-semibold text-sage-800">灵魂合拍指数</h4>
          <p className="text-sm text-sage-600">{soulMatch}</p>
        </div>
      </div>
    </div>
  );
}
