import { create } from 'zustand';
import type { User } from '../types';
import { authApi, clearTokens, loadTokensFromStorage, setTokens } from '../lib/api';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isLoading: boolean;

  initAuth: () => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  accessToken: null,
  refreshToken: null,
  isLoading: false,

  initAuth: async () => {
    const { access, refresh } = loadTokensFromStorage();
    if (!access || !refresh) return;
    setTokens(access, refresh);
    try {
      const user = await authApi.me();
      set({ user, accessToken: access, refreshToken: refresh });
    } catch {
      clearTokens();
      set({ user: null, accessToken: null, refreshToken: null });
    }
  },

  login: async (email, password) => {
    set({ isLoading: true });
    try {
      const data = await authApi.login({ email, password });
      setTokens(data.access_token, data.refresh_token);
      set({ user: data.user, accessToken: data.access_token, refreshToken: data.refresh_token });
    } finally {
      set({ isLoading: false });
    }
  },

  register: async (username, email, password) => {
    set({ isLoading: true });
    try {
      const data = await authApi.register({ username, email, password });
      setTokens(data.access_token, data.refresh_token);
      set({ user: data.user, accessToken: data.access_token, refreshToken: data.refresh_token });
    } finally {
      set({ isLoading: false });
    }
  },

  logout: async () => {
    const { refreshToken } = get();
    if (refreshToken) {
      try { await authApi.logout(refreshToken); } catch { /* ignore */ }
    }
    clearTokens();
    set({ user: null, accessToken: null, refreshToken: null });
  },

  setUser: (user) => set({ user }),
}));
