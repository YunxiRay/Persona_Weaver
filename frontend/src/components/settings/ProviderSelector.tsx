import { PROVIDERS } from "../../pages/Settings";

interface Props {
  selected: string;
  onChange: (v: string) => void;
}

export function ProviderSelector({ selected, onChange }: Props) {
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
      {PROVIDERS.map((p) => (
        <button
          key={p.value}
          type="button"
          onClick={() => onChange(p.value)}
          className={`rounded-xl border-2 px-4 py-3 text-left transition-colors ${
            selected === p.value
              ? "border-warm-500 bg-warm-50"
              : "border-sage-200 bg-white hover:border-sage-300"
          }`}
        >
          <div className="font-medium text-sage-800">{p.label}</div>
          <div className="text-xs text-sage-500">{p.model}</div>
          <a
            href={p.link}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="text-xs text-warm-500 underline"
          >
            获取 Key
          </a>
        </button>
      ))}
    </div>
  );
}
