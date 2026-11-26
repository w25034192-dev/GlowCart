import React from 'react';
import { Link } from 'react-router-dom';
import { Check, ShoppingBag, X } from 'lucide-react';
import { useToastStore } from '@/store/toastStore';
import { getRealFallbackImage, resolveMediaUrl } from '@/utils/media';

export const AtelierBagToast: React.FC = () => {
  const { toast, dismissToast } = useToastStore();

  if (!toast) return null;

  return (
    <div
      role="status"
      aria-live="polite"
      className="fixed bottom-5 right-5 z-50 w-[calc(100vw-2.5rem)] max-w-sm overflow-hidden rounded-2xl border border-primary/20 bg-card/95 p-4 shadow-2xl backdrop-blur-md transition-all duration-200"
    >
      <div className="flex items-start gap-3">
        <img
          src={resolveMediaUrl(toast.imageUrl, toast.name, toast.brand)}
          alt={toast.name}
          className="h-14 w-14 shrink-0 rounded-xl border border-border/60 object-cover bg-beige/40"
          onError={(e) => {
            const target = e.currentTarget;
            if (!target.dataset.fallback) {
              target.dataset.fallback = 'true';
              target.src = getRealFallbackImage(toast.name, toast.brand);
            }
          }}
        />
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-emerald-700">
            <Check className="h-3.5 w-3.5" aria-hidden="true" />
            <span>Added to your Atelier Bag</span>
          </div>
          <p className="mt-0.5 truncate text-sm font-semibold text-foreground">{toast.name}</p>
          <div className="mt-1 flex items-center justify-between gap-2">
            <span className="font-mono text-xs font-bold text-primary">
              {toast.price ? `$${Number(toast.price).toFixed(2)}` : ''}
            </span>
            <Link
              to="/cart"
              onClick={dismissToast}
              className="inline-flex items-center gap-1 rounded-lg bg-primary px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wider text-primary-fg transition-colors hover:bg-primary/90 focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <ShoppingBag className="h-3 w-3" aria-hidden="true" />
              View Bag
            </Link>
          </div>
        </div>
        <button
          type="button"
          onClick={dismissToast}
          aria-label="Dismiss bag notification"
          className="-mr-1 -mt-1 flex h-11 w-11 shrink-0 items-center justify-center rounded-full text-muted-fg transition-colors hover:bg-beige/60 hover:text-foreground focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          <X className="h-4 w-4" aria-hidden="true" />
        </button>
      </div>
    </div>
  );
};
