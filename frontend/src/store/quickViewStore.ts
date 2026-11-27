import { create } from 'zustand';
import type { ProductSummary } from '@/types';

interface QuickViewState {
  product: ProductSummary | null;
  openQuickView: (product: ProductSummary) => void;
  closeQuickView: () => void;
}

export const useQuickViewStore = create<QuickViewState>((set) => ({
  product: null,
  openQuickView: (product) => set({ product }),
  closeQuickView: () => set({ product: null }),
}));
