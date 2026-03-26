import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { dmsApi } from '@/lib/api';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useAuthStore } from '@/store/auth';
import type { DMThread } from '@/types';

interface Props {
  selectedChannelId: string | null;
  onSelect: (channelId: string) => void;
}

export default function DMList({ selectedChannelId, onSelect }: Props) {
  const { t } = useTranslation();
  const user = useAuthStore((s) => s.user);

  const { data: threads = [] } = useQuery<DMThread[]>({
    queryKey: ['dms'],
    queryFn: dmsApi.list,
  });

  function getThreadName(thread: DMThread): string {
    if (thread.name) return thread.name;
    const others = thread.participants.filter((p) => p.id !== user?.id);
    return others.map((p) => p.display_name || p.username).join(', ') || t('nav.direct_messages');
  }

  function getAvatarUrl(thread: DMThread): string | null {
    const others = thread.participants.filter((p) => p.id !== user?.id);
    return others[0]?.avatar_url ?? null;
  }

  return (
    <div className="flex flex-col h-full" style={{ background: 'var(--bg-secondary)' }}>
      <div className="px-3 py-3 flex items-center justify-between border-b" style={{ borderColor: 'var(--border)' }}>
        <span className="text-xs font-semibold uppercase tracking-wide" style={{ color: 'var(--text-secondary)' }}>
          {t('nav.direct_messages')}
        </span>
        <Button
          size="sm"
          variant="ghost"
          className="h-6 w-6 p-0"
          title={t('nav.dms')}
          style={{ color: 'var(--text-secondary)' }}
        >
          +
        </Button>
      </div>
      <ScrollArea className="flex-1">
        <div className="px-2 py-1">
          {threads.length === 0 && (
            <p className="text-xs px-2 py-3 text-center" style={{ color: 'var(--text-muted)' }}>
              {t('nav.dms')}
            </p>
          )}
          {threads.map((thread) => {
            const name = getThreadName(thread);
            const avatarUrl = getAvatarUrl(thread);
            const active = thread.channel_id === selectedChannelId;

            return (
              <button
                key={thread.id}
                onClick={() => onSelect(thread.channel_id)}
                className="w-full flex items-center gap-2 px-2 py-1.5 rounded text-left transition-colors"
                style={{
                  background: active ? 'var(--bg-modifier-selected)' : 'transparent',
                  color: active ? 'var(--text-primary)' : 'var(--text-secondary)',
                }}
              >
                <Avatar className="h-8 w-8 shrink-0">
                  {avatarUrl && <AvatarImage src={avatarUrl} alt={name} />}
                  <AvatarFallback style={{ background: 'var(--accent)', color: '#fff' }}>
                    {name.charAt(0).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{name}</p>
                  {thread.participants.length > 2 && (
                    <p className="text-xs truncate" style={{ color: 'var(--text-muted)' }}>
                      {thread.participants.length} {t('guild.members').toLowerCase()}
                    </p>
                  )}
                </div>
              </button>
            );
          })}
        </div>
      </ScrollArea>
    </div>
  );
}
