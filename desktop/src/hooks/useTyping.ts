import { useRef, useCallback } from 'react';
import { useWebSocketStore } from '../store/ws';

const TYPING_DEBOUNCE_MS = 2500;

/**
 * Returns a function to call on each keystroke in a text channel.
 * Sends TYPING_START over WS, debounced to avoid spamming.
 */
export function useTyping(channelId: string, guildId: string | null) {
  const send = useWebSocketStore((s) => s.send);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const onKeystroke = useCallback(() => {
    if (timerRef.current) return; // already sent recently
    send('TYPING_START', { channel_id: channelId, ...(guildId ? { guild_id: guildId } : {}) });
    timerRef.current = setTimeout(() => {
      timerRef.current = null;
    }, TYPING_DEBOUNCE_MS);
  }, [channelId, guildId, send]);

  return { onKeystroke };
}
