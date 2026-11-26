import { create } from 'zustand';

export interface BagToastItem {
  id: string;
  name: string;
  brand: string;
  imageUrl?: string | null;
  price?: string | number | null;
}

interface ToastState {
  toast: BagToastItem | null;
  showBagToast: (item: Omit<BagToastItem, 'id'>) => void;
  dismissToast: () => void;
}

let dismissTimer: ReturnType<typeof setTimeout> | null = null;

export const useToastStore = create<ToastState>((set) => ({
  toast: null,
  showBagToast: (item) => {
    if (dismissTimer) {
      clearTimeout(dismissTimer);
    }
    const id = `${Date.now()}`;
    set({ toast: { ...item, id } });
    dismissTimer = setTimeout(() => {
      set((state) => (state.toast?.id === id ? { toast: null } : state));
    }, 4200);
  },
  dismissToast: () => {
    if (dismissTimer) {
      clearTimeout(dismissTimer);
      dismissTimer = null;
    }
    set({ toast: null });
  },
}));
