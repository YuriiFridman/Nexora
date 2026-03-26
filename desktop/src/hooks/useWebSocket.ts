import { useEffect, useCallback } from 'react';
import { useWebSocketStore } from '../store/ws';

type Handler = (data: unknown) => void;

/**
 * Subscribe to WebSocket events. Automatically cleans up on unmount.
 */
export function useWebSocket(event: string, handler: Handler) {
  const on = useWebSocketStore((s) => s.on);
  const off = useWebSocketStore((s) => s.off);

  // Stable reference to handler to avoid re-subscribing on every render
  const stableHandler = useCallback(handler, []); // eslint-disable-line

  useEffect(() => {
    on(event, stableHandler);
    return () => off(event, stableHandler);
  }, [event, stableHandler, on, off]);
}

export { useWebSocketStore };
