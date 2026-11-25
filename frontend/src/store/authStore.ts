import { create } from 'zustand';
import { authApi } from '@/services/api';
import type { User } from '@/types';

interface AuthState {
  user: User | null;
  isLoading: boolean;
  setSession: (accessToken: string, refreshToken: string, user: User) => void;
  clearSession: () => void;
  hydrate: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: Boolean(localStorage.getItem('glowcart_access_token')),
  setSession: (accessToken, refreshToken, user) => {
    localStorage.setItem('glowcart_access_token', accessToken);
    localStorage.setItem('glowcart_refresh_token', refreshToken);
    set({ user, isLoading: false });
  },
  clearSession: () => {
    localStorage.removeItem('glowcart_access_token');
    localStorage.removeItem('glowcart_refresh_token');
    set({ user: null, isLoading: false });
  },
  hydrate: async () => {
    const token = localStorage.getItem('glowcart_access_token');
    if (!token) {
      set({ user: null, isLoading: false });
      return;
    }
    try {
      const user = await authApi.me();
      set({ user, isLoading: false });
    } catch {
      localStorage.removeItem('glowcart_access_token');
      localStorage.removeItem('glowcart_refresh_token');
      set({ user: null, isLoading: false });
    }
  },
}));

