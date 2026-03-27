import type { Role } from '@/types';
import { Button } from '@/components/ui/button';

interface Props {
  role: Role;
  membersCount: number;
  active: boolean;
  onSelect: () => void;
  onMoveUp: () => void;
  onMoveDown: () => void;
  onDuplicate: () => void;
  onDelete: () => void;
}

function toHex(color: number) {
  return `#${Math.max(0, Math.min(0xFFFFFF, color)).toString(16).padStart(6, '0')}`;
}

export default function RoleItem({
  role,
  membersCount,
  active,
  onSelect,
  onMoveUp,
  onMoveDown,
  onDuplicate,
  onDelete,
}: Props) {
  return (
    <div
      className={`rounded-lg border p-3 transition-all ${
        active
          ? 'border-[var(--accent)] bg-[var(--bg-primary)] shadow-[0_8px_20px_rgba(0,0,0,0.2)]'
          : 'border-white/10 bg-[var(--bg-primary)]/65 hover:border-white/20 hover:bg-[var(--bg-primary)]'
      }`}
    >
      <button
        type="button"
        onClick={onSelect}
        className="flex w-full items-center justify-between text-left"
        aria-label={`Select role ${role.name}`}
      >
        <span className="flex items-center gap-2">
          <span className="text-lg" style={{ color: toHex(role.color) }}>●</span>
          <span>
            <span className="block text-sm font-semibold text-[var(--text-primary)]">
              {role.icon_emoji ? `${role.icon_emoji} ` : ''}
              {role.name}
            </span>
            <span className="block text-xs text-[var(--text-muted)]">
              #{role.position} • {membersCount} members
            </span>
          </span>
        </span>
        {role.mentionable && (
          <span className="rounded bg-[var(--accent)]/15 px-2 py-0.5 text-xs text-[var(--accent)]">@mention</span>
        )}
      </button>
      {!role.is_default && (
        <div className="mt-2 flex gap-1">
          <Button size="sm" variant="ghost" onClick={onMoveUp} aria-label={`Move ${role.name} up`}>↑</Button>
          <Button size="sm" variant="ghost" onClick={onMoveDown} aria-label={`Move ${role.name} down`}>↓</Button>
          <Button size="sm" variant="ghost" onClick={onDuplicate}>Duplicate</Button>
          <Button size="sm" variant="ghost" onClick={onDelete}>Delete</Button>
        </div>
      )}
    </div>
  );
}
