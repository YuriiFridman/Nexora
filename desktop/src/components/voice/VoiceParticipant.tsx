import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import type { User } from '@/types';

interface Props {
  user: User;
  isMuted: boolean;
  isDeafened: boolean;
  isSpeaking: boolean;
  isLocal: boolean;
}

export default function VoiceParticipantItem({ user, isMuted, isDeafened, isSpeaking, isLocal }: Props) {
  const name = user.display_name || user.username;
  return (
    <div
      className="flex flex-col items-center gap-2 p-3 rounded-lg"
      style={{ background: 'var(--bg-secondary)' }}
    >
      <div className="relative">
        <div
          className="rounded-full p-0.5 transition-all"
          style={{
            boxShadow: isSpeaking ? '0 0 0 2px var(--online)' : 'none',
          }}
        >
          <Avatar className="w-12 h-12">
            {user.avatar_url ? (
              <img src={user.avatar_url} alt={name} className="w-full h-full object-cover rounded-full" />
            ) : (
              <AvatarFallback style={{ background: 'var(--bg-tertiary)', color: 'var(--text-primary)' }}>
                {name.charAt(0).toUpperCase()}
              </AvatarFallback>
            )}
          </Avatar>
        </div>
        {/* Status icons */}
        <div className="absolute -bottom-1 -right-1 flex gap-0.5">
          {isMuted && (
            <span className="text-xs rounded-full px-0.5" style={{ background: 'var(--bg-primary)', color: 'var(--danger)' }}>
              🔇
            </span>
          )}
          {isDeafened && (
            <span className="text-xs rounded-full px-0.5" style={{ background: 'var(--bg-primary)', color: 'var(--danger)' }}>
              🔕
            </span>
          )}
        </div>
      </div>
      <div className="text-xs text-center truncate w-full" style={{ color: isLocal ? 'var(--accent)' : 'var(--text-secondary)' }}>
        {name}{isLocal ? ' (you)' : ''}
      </div>
    </div>
  );
}
