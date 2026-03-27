import { Input } from '@/components/ui/input';

const PRESET_COLORS = [
  0xED4245,
  0xFEE75C,
  0x57F287,
  0x5865F2,
  0xEB459E,
  0x9B84EE,
  0x1ABC9C,
  0x95A5A6,
];

interface Props {
  value: number;
  onChange: (value: number) => void;
}

function toHex(color: number) {
  return `#${Math.max(0, Math.min(0xFFFFFF, color)).toString(16).padStart(6, '0')}`;
}

export default function ColorPicker({ value, onChange }: Props) {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <input
          type="color"
          value={toHex(value)}
          onChange={(e) => onChange(parseInt(e.target.value.slice(1), 16))}
          aria-label="Role color"
          className="h-10 w-12 cursor-pointer rounded border border-white/15 bg-transparent"
        />
        <Input
          value={toHex(value)}
          onChange={(e) => onChange(parseInt(e.target.value.replace('#', ''), 16) || 0)}
          placeholder="#5865F2"
          maxLength={7}
        />
      </div>
      <div className="flex flex-wrap gap-1">
        {PRESET_COLORS.map((color) => (
          <button
            key={color}
            type="button"
            onClick={() => onChange(color)}
            aria-label={`Set role color ${toHex(color)}`}
            className="h-6 w-6 rounded-full border border-white/15 transition-transform hover:scale-110"
            style={{ backgroundColor: toHex(color) }}
          />
        ))}
        <button
          type="button"
          onClick={() => onChange(0)}
          className="rounded-md border border-white/15 px-2 text-xs text-[var(--text-secondary)] hover:bg-white/10"
        >
          Reset
        </button>
      </div>
    </div>
  );
}
