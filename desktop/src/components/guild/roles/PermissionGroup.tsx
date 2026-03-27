import type { PermissionEntry } from '@/types';
import { Button } from '@/components/ui/button';

interface Props {
  category: string;
  permissions: PermissionEntry[];
  selectedMask: number;
  onTogglePermission: (value: number, enabled: boolean) => void;
  onSelectAll: () => void;
  onClearAll: () => void;
}

export default function PermissionGroup({
  category,
  permissions,
  selectedMask,
  onTogglePermission,
  onSelectAll,
  onClearAll,
}: Props) {
  return (
    <section className="space-y-2 rounded-lg border border-white/10 bg-[var(--bg-primary)] p-3">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">{category}</h4>
        <div className="flex gap-1">
          <Button size="sm" variant="ghost" onClick={onSelectAll}>All</Button>
          <Button size="sm" variant="ghost" onClick={onClearAll}>None</Button>
        </div>
      </div>
      <div className="space-y-2">
        {permissions.map((perm) => {
          const checked = Boolean(selectedMask & perm.value);
          return (
            <label
              key={perm.key}
              className={`flex cursor-pointer items-start gap-2 rounded-md p-2 transition-colors ${
                perm.critical ? 'border border-[var(--danger)]/30 bg-[var(--danger)]/10' : 'hover:bg-white/5'
              }`}
            >
              <input
                type="checkbox"
                checked={checked}
                onChange={(e) => onTogglePermission(perm.value, e.target.checked)}
                aria-label={perm.label}
              />
              <span className="block">
                <span className="block text-sm text-[var(--text-primary)]">{perm.label}</span>
                <span className="block text-xs text-[var(--text-muted)]">{perm.description}</span>
              </span>
            </label>
          );
        })}
      </div>
    </section>
  );
}
