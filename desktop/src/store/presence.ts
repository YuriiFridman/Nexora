import { create } from 'zustand';
import type { PresenceStatus } from '../types';

interface PresenceState {
  // userId -> status
  statuses: Map<string, PresenceStatus>;
  setStatus: (userId: string, status: PresenceStatus) => void;
  getStatus: (userId: string) => PresenceStatus;
  bulkSet: (entries: Array<{ userId: string; status: PresenceStatus }>) => void;
}

export const usePresenceStore = create<PresenceState>((set, get) => ({
  statuses: new Map(),

  setStatus: (userId, status) => {
    const statuses = new Map(get().statuses);
    statuses.set(userId, status);
    set({ statuses });
  },

  getStatus: (userId) => {
    return get().statuses.get(userId) ?? 'offline';
  },

  bulkSet: (entries) => {
    const statuses = new Map(get().statuses);
    for (const { userId, status } of entries) {
      statuses.set(userId, status);
    }
    set({ statuses });
  },
}));
