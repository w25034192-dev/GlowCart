import { create } from 'zustand';
import { cartApi } from '@/services/api';
import type { CartResponse } from '@/types';

interface CartState {
  cart: CartResponse | null;
  itemCount: number;
  fetchCart: (couponCode?: string) => Promise<void>;
  setCart: (cart: CartResponse) => void;
  resetCart: () => void;
}

export const useCartStore = create<CartState>((set) => ({
  cart: null,
  itemCount: 0,
  fetchCart: async (couponCode) => {
    try {
      const cart = await cartApi.getCart(couponCode);
      const itemCount = cart.items.reduce((sum, i) => sum + i.quantity, 0);
      set({ cart, itemCount });
    } catch {
      set({ cart: null, itemCount: 0 });
    }
  },
  setCart: (cart) => {
    const itemCount = cart.items.reduce((sum, i) => sum + i.quantity, 0);
    set({ cart, itemCount });
  },
  resetCart: () => set({ cart: null, itemCount: 0 }),
}));

