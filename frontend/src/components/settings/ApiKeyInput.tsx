interface Props {
  value: string;
  onChange: (v: string) => void;
}

export function ApiKeyInput({ value, onChange }: Props) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium text-sage-700">
        API Key <span className="text-red-400">*</span>
      </label>
      <input
        type="password"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="sk-..."
        className="w-full rounded-xl border border-sage-200 px-4 py-2.5 text-sage-800 placeholder-sage-300 focus:border-warm-400 focus:outline-none"
      />
    </div>
  );
}
