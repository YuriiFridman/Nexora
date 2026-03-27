import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { guildsApi, rolesApi } from '@/lib/api';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import type { Guild, GuildMember, MemberRole, PermissionEntry, Role, RoleAuditLog } from '@/types';
import RoleItem from './roles/RoleItem';
import RoleEditorPanel from './roles/RoleEditorPanel';

interface Props {
  guild: Guild;
  onClose: () => void;
}

export default function GuildSettings({ guild, onClose }: Props) {
  const { t } = useTranslation();
  const qc = useQueryClient();
  const [tab, setTab] = useState<'overview' | 'roles'>('overview');
  const [name, setName] = useState(guild.name);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [search, setSearch] = useState('');
  const [newRoleName, setNewRoleName] = useState('');
  const [roleName, setRoleName] = useState('');
  const [roleColor, setRoleColor] = useState(0);
  const [roleEmoji, setRoleEmoji] = useState('');
  const [roleHoist, setRoleHoist] = useState(false);
  const [roleMentionable, setRoleMentionable] = useState(false);
  const [rolePermissions, setRolePermissions] = useState(0);
  const [selectedRoleId, setSelectedRoleId] = useState<string>('');
  const [selectedUserId, setSelectedUserId] = useState<string[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');

  const save = useMutation({
    mutationFn: () => guildsApi.update(guild.id, { name }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['guilds'] });
      setError('');
      onClose();
    },
    onError: (e: Error) => setError(e.message),
  });

  const { data: roles = [] } = useQuery<Role[]>({
    queryKey: ['roles', guild.id],
    queryFn: () => rolesApi.list(guild.id),
  });
  const { data: members = [] } = useQuery<GuildMember[]>({
    queryKey: ['guildMembers', guild.id],
    queryFn: () => guildsApi.members(guild.id),
  });
  const { data: memberRoles = [] } = useQuery<MemberRole[]>({
    queryKey: ['memberRoles', guild.id],
    queryFn: () => rolesApi.listMemberRoles(guild.id),
  });
  const { data: roleTemplates = [] } = useQuery<string[]>({
    queryKey: ['roleTemplates'],
    queryFn: () => rolesApi.listTemplates(),
  });
  const { data: permissionsMeta = [] } = useQuery<PermissionEntry[]>({
    queryKey: ['permissionsMeta'],
    queryFn: () => rolesApi.listPermissions(),
  });
  const { data: roleAudit = [] } = useQuery<RoleAuditLog[]>({
    queryKey: ['roleAudit', guild.id],
    queryFn: () => rolesApi.listAudit(guild.id),
    retry: false,
  });

  const createRole = useMutation({
    mutationFn: () =>
      rolesApi.create(guild.id, {
        name: newRoleName.trim(),
        color: roleColor,
        permissions: rolePermissions,
        mentionable: roleMentionable,
        icon_emoji: roleEmoji || null,
        hoist: roleHoist,
        position: roles.length,
      }),
    onSuccess: () => {
      setNewRoleName('');
      setRoleColor(0);
      setRoleEmoji('');
      setRoleHoist(false);
      setRoleMentionable(false);
      setRolePermissions(0);
      setNotice('Role created');
      qc.invalidateQueries({ queryKey: ['roles', guild.id] });
    },
    onError: (e: Error) => setError(e.message),
  });

  const updateRole = useMutation({
    mutationFn: (payload: { role: Role; patch: Partial<Role> }) => rolesApi.update(guild.id, payload.role.id, payload.patch),
    onSuccess: () => {
      setNotice('Role updated');
      qc.invalidateQueries({ queryKey: ['roles', guild.id] });
      qc.invalidateQueries({ queryKey: ['roleAudit', guild.id] });
    },
    onError: (e: Error) => setError(e.message),
  });

  const duplicateRole = useMutation({
    mutationFn: (roleId: string) => rolesApi.duplicate(guild.id, roleId),
    onSuccess: () => {
      setNotice('Role duplicated');
      qc.invalidateQueries({ queryKey: ['roles', guild.id] });
      qc.invalidateQueries({ queryKey: ['roleAudit', guild.id] });
    },
    onError: (e: Error) => setError(e.message),
  });

  const deleteRole = useMutation({
    mutationFn: (roleId: string) => rolesApi.delete(guild.id, roleId),
    onSuccess: () => {
      setNotice('Role deleted');
      qc.invalidateQueries({ queryKey: ['roles', guild.id] });
      qc.invalidateQueries({ queryKey: ['memberRoles', guild.id] });
      qc.invalidateQueries({ queryKey: ['roleAudit', guild.id] });
      if (selectedRoleId) setSelectedRoleId('');
    },
    onError: (e: Error) => setError(e.message),
  });

  const moveRole = useMutation({
    mutationFn: (nextRoles: Role[]) => rolesApi.reorder(guild.id, nextRoles.map((role, idx) => ({ role_id: role.id, position: nextRoles.length - idx }))),
    onSuccess: () => {
      setNotice('Role order updated');
      qc.invalidateQueries({ queryKey: ['roles', guild.id] });
      qc.invalidateQueries({ queryKey: ['roleAudit', guild.id] });
    },
    onError: (e: Error) => setError(e.message),
  });

  const createFromTemplate = useMutation({
    mutationFn: () => rolesApi.createFromTemplate(guild.id, { template: selectedTemplate, position: roles.length }),
    onSuccess: () => {
      setNotice('Template role created');
      setSelectedTemplate('');
      qc.invalidateQueries({ queryKey: ['roles', guild.id] });
      qc.invalidateQueries({ queryKey: ['roleAudit', guild.id] });
    },
    onError: (e: Error) => setError(e.message),
  });

  const bulkAssign = useMutation({
    mutationFn: () => rolesApi.bulkAssign(guild.id, selectedRoleId, selectedUserId),
    onSuccess: () => {
      setNotice('Members updated');
      qc.invalidateQueries({ queryKey: ['memberRoles', guild.id] });
      setSelectedRoleId('');
      setSelectedUserId([]);
    },
    onError: (e: Error) => setError(e.message),
  });

  const bulkRemove = useMutation({
    mutationFn: () => rolesApi.bulkRemove(guild.id, selectedRoleId, selectedUserId),
    onSuccess: () => {
      setNotice('Members updated');
      qc.invalidateQueries({ queryKey: ['memberRoles', guild.id] });
      setSelectedRoleId('');
      setSelectedUserId([]);
    },
    onError: (e: Error) => setError(e.message),
  });

  const memberRoleCountByRole = useMemo(() => {
    const counts = new Map<string, number>();
    for (const mr of memberRoles) counts.set(mr.role_id, (counts.get(mr.role_id) ?? 0) + 1);
    return counts;
  }, [memberRoles]);
  const selectedRole = useMemo(() => roles.find((role) => role.id === selectedRoleId) ?? null, [roles, selectedRoleId]);
  const filteredRoles = useMemo(
    () => roles.filter((role) => role.name.toLowerCase().includes(search.trim().toLowerCase())),
    [roles, search],
  );
  const roleMembers = useMemo(
    () => new Set(memberRoles.filter((entry) => entry.role_id === selectedRoleId).map((entry) => entry.user_id)),
    [memberRoles, selectedRoleId],
  );

  useEffect(() => {
    if (!selectedRoleId && roles.length) setSelectedRoleId(roles[0].id);
  }, [roles, selectedRoleId]);

  useEffect(() => {
    if (!selectedRole) return;
    setRoleName(selectedRole.name);
    setRoleColor(selectedRole.color ?? 0);
    setRoleEmoji(selectedRole.icon_emoji ?? '');
    setRoleHoist(Boolean(selectedRole.hoist));
    setRoleMentionable(Boolean(selectedRole.mentionable));
    setRolePermissions(selectedRole.permissions ?? 0);
  }, [selectedRole]);

  useEffect(() => {
    if (!notice) return;
    const timer = window.setTimeout(() => setNotice(''), 1800);
    return () => window.clearTimeout(timer);
  }, [notice]);

  const canSaveRole =
    !!selectedRole && (
      selectedRole.name !== roleName.trim() ||
      selectedRole.color !== roleColor ||
      (selectedRole.icon_emoji ?? '') !== roleEmoji ||
      Boolean(selectedRole.hoist) !== roleHoist ||
      Boolean(selectedRole.mentionable) !== roleMentionable ||
      selectedRole.permissions !== rolePermissions
    );

  const handleMoveRole = (roleId: string, direction: -1 | 1) => {
    const index = roles.findIndex((role) => role.id === roleId);
    const target = index + direction;
    if (index < 0 || target < 0 || target >= roles.length) return;
    const next = [...roles];
    [next[index], next[target]] = [next[target], next[index]];
    moveRole.mutate(next);
  };

  const togglePermission = (mask: number, enabled: boolean) => {
    setRolePermissions((current) => (enabled ? current | mask : current & ~mask));
  };

  return (
    <Dialog open onOpenChange={(v) => !v && onClose()}>
      <DialogContent
        style={{ background: 'var(--bg-secondary)', border: '1px solid rgba(255,255,255,0.08)', color: 'var(--text-primary)' }}
        className="max-w-6xl"
      >
        <DialogHeader>
          <DialogTitle style={{ color: 'var(--text-primary)' }}>{t('guild.settings')}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 max-h-[78vh] overflow-y-auto">
          <div className="flex gap-2">
            <Button variant={tab === 'overview' ? 'default' : 'ghost'} onClick={() => setTab('overview')}>
              {t('guild.settings_overview')}
            </Button>
            <Button variant={tab === 'roles' ? 'default' : 'ghost'} onClick={() => setTab('roles')}>
              {t('guild.roles')}
            </Button>
          </div>

          {tab === 'overview' && (
            <div className="space-y-4">
              <div>
                <label className="text-xs font-semibold uppercase mb-1 block" style={{ color: 'var(--text-muted)' }}>
                  {t('guild.server_name')}
                </label>
                <Input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  maxLength={100}
                  style={{ background: 'var(--bg-primary)', border: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-primary)' }}
                />
              </div>
            </div>
          )}

          {tab === 'roles' && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 gap-4 xl:grid-cols-[340px_1fr]">
                <aside className="space-y-3 rounded-xl border border-white/10 bg-[var(--bg-secondary)] p-3">
                  <div className="space-y-2 rounded-lg border border-white/10 bg-[var(--bg-primary)] p-3">
                    <p className="text-sm font-semibold">{t('guild.create_role')}</p>
                    <div className="space-y-2">
                      <Input
                        value={newRoleName}
                        onChange={(e) => setNewRoleName(e.target.value)}
                        placeholder={t('guild.role_name')}
                        maxLength={100}
                      />
                      <Button
                        onClick={() => createRole.mutate()}
                        disabled={!newRoleName.trim() || createRole.isPending}
                        style={{ background: 'var(--accent)', color: '#fff' }}
                      >
                        {createRole.isPending ? t('common.loading') : t('common.create')}
                      </Button>
                    </div>
                    <div className="pt-2">
                      <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">Role template</p>
                      <div className="flex gap-2">
                        <select
                          value={selectedTemplate}
                          onChange={(e) => setSelectedTemplate(e.target.value)}
                          className="h-9 flex-1 rounded-md border border-white/10 bg-[var(--bg-tertiary)] px-2 text-sm text-[var(--text-primary)]"
                          aria-label="Role template"
                        >
                          <option value="">Choose template</option>
                          {roleTemplates.map((template) => (
                            <option key={template} value={template}>
                              {template}
                            </option>
                          ))}
                        </select>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => createFromTemplate.mutate()}
                          disabled={!selectedTemplate || createFromTemplate.isPending}
                        >
                          Apply
                        </Button>
                      </div>
                    </div>
                  </div>

                  <div className="rounded-lg border border-white/10 bg-[var(--bg-primary)] p-3">
                    <Input
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                      placeholder={t('common.search')}
                      aria-label="Search roles"
                    />
                    <div className="mt-2 max-h-[320px] space-y-2 overflow-y-auto">
                      {!roles.length && (
                        <div className="space-y-2">
                          {[1, 2, 3].map((item) => (
                            <div key={item} className="h-14 animate-pulse rounded-md bg-white/10" />
                          ))}
                        </div>
                      )}
                      {filteredRoles.map((role) => (
                        <RoleItem
                          key={role.id}
                          role={role}
                          membersCount={memberRoleCountByRole.get(role.id) ?? 0}
                          active={selectedRoleId === role.id}
                          onSelect={() => setSelectedRoleId(role.id)}
                          onMoveUp={() => handleMoveRole(role.id, -1)}
                          onMoveDown={() => handleMoveRole(role.id, 1)}
                          onDuplicate={() => duplicateRole.mutate(role.id)}
                          onDelete={() => deleteRole.mutate(role.id)}
                        />
                      ))}
                      {roles.length > 0 && !filteredRoles.length && (
                        <p className="rounded-md border border-dashed border-white/15 p-3 text-sm text-[var(--text-muted)]">
                          No roles match this filter.
                        </p>
                      )}
                    </div>
                  </div>
                </aside>

                <section className="space-y-3">
                  <RoleEditorPanel
                    role={selectedRole}
                    roleName={roleName}
                    roleEmoji={roleEmoji}
                    roleColor={roleColor}
                    roleMentionable={roleMentionable}
                    roleHoist={roleHoist}
                    rolePermissions={rolePermissions}
                    permissionsMeta={permissionsMeta}
                    savePending={updateRole.isPending}
                    onRoleNameChange={setRoleName}
                    onRoleEmojiChange={setRoleEmoji}
                    onRoleColorChange={setRoleColor}
                    onRoleMentionableChange={setRoleMentionable}
                    onRoleHoistChange={setRoleHoist}
                    onTogglePermission={togglePermission}
                    onSave={() => {
                      if (!selectedRole) return;
                      updateRole.mutate({
                        role: selectedRole,
                        patch: {
                          name: roleName.trim(),
                          color: roleColor,
                          icon_emoji: roleEmoji || null,
                          hoist: roleHoist,
                          mentionable: roleMentionable,
                          permissions: rolePermissions,
                        },
                      });
                    }}
                  />

                  <div className="rounded-xl border border-white/10 bg-[var(--bg-secondary)] p-3">
                    <p className="mb-2 text-sm font-semibold">Bulk member role update</p>
                    <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
                      <select
                        value={selectedRoleId}
                        onChange={(e) => setSelectedRoleId(e.target.value)}
                        className="h-9 rounded-md px-2 text-sm"
                        style={{ background: 'var(--bg-tertiary)', color: 'var(--text-primary)' }}
                      >
                        <option value="">{t('guild.select_role')}</option>
                        {roles.filter((r) => !r.is_default).map((r) => <option key={r.id} value={r.id}>{r.name}</option>)}
                      </select>
                      <div className="max-h-28 overflow-y-auto rounded-md border border-white/10 bg-[var(--bg-primary)] p-2">
                        {members.map((member) => {
                          const checked = selectedUserId.includes(member.user_id);
                          const currentlyHas = roleMembers.has(member.user_id);
                          return (
                            <label key={member.user_id} className="flex items-center justify-between gap-2 py-1 text-sm">
                              <span className="text-[var(--text-primary)]">
                                {member.user.display_name || member.user.username}
                                {currentlyHas ? <span className="ml-1 text-xs text-[var(--text-muted)]">(has role)</span> : null}
                              </span>
                              <input
                                type="checkbox"
                                checked={checked}
                                onChange={(e) => setSelectedUserId((current) => (
                                  e.target.checked
                                    ? [...current, member.user_id]
                                    : current.filter((id) => id !== member.user_id)
                                ))}
                                aria-label={`Select member ${member.user.username}`}
                              />
                            </label>
                          );
                        })}
                      </div>
                    </div>
                    <div className="mt-2 flex gap-2">
                      <Button
                        onClick={() => bulkAssign.mutate()}
                        disabled={!selectedRoleId || !selectedUserId.length || bulkAssign.isPending}
                        style={{ background: 'var(--accent)', color: '#fff' }}
                      >
                        Assign selected
                      </Button>
                      <Button
                        variant="ghost"
                        onClick={() => bulkRemove.mutate()}
                        disabled={!selectedRoleId || !selectedUserId.length || bulkRemove.isPending}
                      >
                        Remove selected
                      </Button>
                    </div>
                  </div>

                  <div className="rounded-xl border border-white/10 bg-[var(--bg-secondary)] p-3">
                    <p className="mb-2 text-sm font-semibold">Role change history</p>
                    <div className="max-h-32 space-y-1 overflow-y-auto text-sm">
                      {!roleAudit.length && <p className="text-[var(--text-muted)]">No audit events yet.</p>}
                      {roleAudit.slice(0, 20).map((event) => (
                        <p key={event.id} className="rounded-md bg-[var(--bg-primary)] px-2 py-1 text-[var(--text-secondary)]">
                          <span className="font-semibold text-[var(--text-primary)]">{event.action}</span> — {event.details ?? 'No details'}
                        </p>
                      ))}
                    </div>
                  </div>
                </section>
              </div>

            </div>
          )}

          {error && <p className="text-sm" style={{ color: 'var(--danger)' }}>{error}</p>}
          {notice && <p className="text-sm" style={{ color: 'var(--success)' }}>{notice}</p>}

          <div className="flex justify-end gap-2 pt-2">
            <Button variant="ghost" onClick={onClose} style={{ color: 'var(--text-secondary)' }}>
              {t('common.cancel')}
            </Button>
            {tab === 'overview' && (
              <Button
                onClick={() => save.mutate()}
                disabled={!name.trim() || save.isPending}
                style={{ background: 'var(--accent)', color: '#fff' }}
              >
                {save.isPending ? t('common.loading') : t('common.save')}
              </Button>
            )}
            {tab === 'roles' && (
              <Button
                onClick={() => {
                  if (!selectedRole) return;
                  updateRole.mutate({
                    role: selectedRole,
                    patch: {
                      name: roleName.trim(),
                      color: roleColor,
                      icon_emoji: roleEmoji || null,
                      hoist: roleHoist,
                      mentionable: roleMentionable,
                      permissions: rolePermissions,
                    },
                  });
                }}
                disabled={!selectedRole || !roleName.trim() || updateRole.isPending || !canSaveRole}
                style={{ background: 'var(--accent)', color: '#fff' }}
              >
                {updateRole.isPending ? t('common.loading') : t('common.save')}
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
