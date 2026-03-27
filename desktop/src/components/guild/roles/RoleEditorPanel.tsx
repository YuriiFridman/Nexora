import { useMemo } from 'react';
import type { PermissionEntry, Role } from '@/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import PermissionGroup from './PermissionGroup';
import ColorPicker from './ColorPicker';

interface Props {
  role: Role | null;
  roleName: string;
  roleEmoji: string;
  roleColor: number;
  roleMentionable: boolean;
  roleHoist: boolean;
  rolePermissions: number;
  permissionsMeta: PermissionEntry[];
  savePending: boolean;
  onRoleNameChange: (value: string) => void;
  onRoleEmojiChange: (value: string) => void;
  onRoleColorChange: (value: number) => void;
  onRoleMentionableChange: (value: boolean) => void;
  onRoleHoistChange: (value: boolean) => void;
  onTogglePermission: (value: number, enabled: boolean) => void;
  onSave: () => void;
}

export default function RoleEditorPanel({
  role,
  roleName,
  roleEmoji,
  roleColor,
  roleMentionable,
  roleHoist,
  rolePermissions,
  permissionsMeta,
  savePending,
  onRoleNameChange,
  onRoleEmojiChange,
  onRoleColorChange,
  onRoleMentionableChange,
  onRoleHoistChange,
  onTogglePermission,
  onSave,
}: Props) {
  const permissionsByCategory = useMemo(() => {
    const grouped = new Map<string, PermissionEntry[]>();
    for (const permission of permissionsMeta) {
      const list = grouped.get(permission.category) ?? [];
      list.push(permission);
      grouped.set(permission.category, list);
    }
    return Array.from(grouped.entries());
  }, [permissionsMeta]);

  if (!role) {
    return (
      <div className="flex h-full min-h-[420px] items-center justify-center rounded-xl border border-dashed border-white/15 bg-[var(--bg-primary)]/35 p-6 text-center">
        <div>
          <p className="text-base font-semibold text-[var(--text-primary)]">Select a role to configure details</p>
          <p className="mt-1 text-sm text-[var(--text-muted)]">
            Use the left panel to pick or create a role. Detailed settings will appear here.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3 rounded-xl border border-white/10 bg-[var(--bg-secondary)] p-4">
      <div className="rounded-lg border border-white/10 bg-[var(--bg-primary)] p-3">
        <p className="text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">Role Preview</p>
        <p className="mt-2 text-lg font-semibold" style={{ color: `#${roleColor.toString(16).padStart(6, '0')}` }}>
          {roleEmoji ? `${roleEmoji} ` : ''}{roleName || 'Unnamed role'}
        </p>
      </div>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        <div className="space-y-2">
          <label className="text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">Role name</label>
          <Input value={roleName} onChange={(e) => onRoleNameChange(e.target.value)} maxLength={100} />
        </div>
        <div className="space-y-2">
          <label className="text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">Role icon / emoji</label>
          <Input value={roleEmoji} onChange={(e) => onRoleEmojiChange(e.target.value)} maxLength={32} placeholder="🔥" />
        </div>
      </div>

      <div className="space-y-2">
        <label className="text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">Color</label>
        <ColorPicker value={roleColor} onChange={onRoleColorChange} />
      </div>

      <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
        <label className="flex items-center gap-2 rounded-md border border-white/10 bg-[var(--bg-primary)] p-2 text-sm text-[var(--text-primary)]">
          <input type="checkbox" checked={roleMentionable} onChange={(e) => onRoleMentionableChange(e.target.checked)} />
          Allow mentions
        </label>
        <label className="flex items-center gap-2 rounded-md border border-white/10 bg-[var(--bg-primary)] p-2 text-sm text-[var(--text-primary)]">
          <input type="checkbox" checked={roleHoist} onChange={(e) => onRoleHoistChange(e.target.checked)} />
          Display separately
        </label>
      </div>

      <div className="space-y-2">
        {permissionsByCategory.map(([category, items]) => {
          const mask = items.reduce((acc, item) => acc | item.value, 0);
          return (
            <PermissionGroup
              key={category}
              category={category}
              permissions={items}
              selectedMask={rolePermissions}
              onTogglePermission={onTogglePermission}
              onSelectAll={() => onTogglePermission(mask, true)}
              onClearAll={() => onTogglePermission(mask, false)}
            />
          );
        })}
      </div>

      <div className="flex justify-end">
        <Button onClick={onSave} disabled={!roleName.trim() || savePending}>
          {savePending ? 'Saving…' : 'Save role'}
        </Button>
      </div>
    </div>
  );
}
