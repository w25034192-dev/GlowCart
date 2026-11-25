import React from 'react';
import { AlertCircle, Star } from 'lucide-react';

export const Button: React.FC<
  React.ButtonHTMLAttributes<HTMLButtonElement> & {
    variant?: 'primary' | 'secondary' | 'outline' | 'danger' | 'accent';
  }
> = ({ variant = 'primary', className = '', children, ...props }) => {
  const styles: Record<string, string> = {
    primary: 'bg-primary text-primary-fg hover:opacity-90',
    accent: 'bg-accent text-accent-fg hover:opacity-90',
    secondary: 'bg-blush text-foreground border border-border hover:bg-beige',
    outline: 'border border-border bg-card text-foreground hover:bg-muted/60',
    danger: 'bg-destructive text-white hover:opacity-90',
  };
  return (
    <button
      {...props}
      className={`touch-target inline-flex cursor-pointer items-center justify-center gap-2 rounded-lg px-5 py-2.5 text-sm font-semibold transition-opacity duration-200 disabled:cursor-not-allowed disabled:opacity-50 ${styles[variant]} ${className}`}
    >
      {children}
    </button>
  );
};

export const Card: React.FC<{ className?: string; children: React.ReactNode }> = ({
  className = '',
  children,
}) => (
  <div className={`rounded-xl border border-border bg-card p-6 shadow-sm ${className}`}>
    {children}
  </div>
);

export const Badge: React.FC<{
  tone?: 'neutral' | 'blush' | 'success' | 'warning' | 'danger';
  children: React.ReactNode;
}> = ({ tone = 'neutral', children }) => {
  const styles: Record<string, string> = {
    neutral: 'bg-muted text-foreground',
    blush: 'bg-blush text-foreground',
    success: 'bg-emerald-100 text-emerald-950',
    warning: 'bg-amber-100 text-amber-950',
    danger: 'bg-red-100 text-red-950',
  };
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${styles[tone]}`}
    >
      {children}
    </span>
  );
};

export const AlertBox: React.FC<{ message: string; tone?: 'error' | 'info' }> = ({
  message,
  tone = 'error',
}) => (
  <div
    role="alert"
    className={`flex items-start gap-2 rounded-lg border p-3.5 text-sm ${
      tone === 'error'
        ? 'border-red-300 bg-red-50 text-red-950'
        : 'border-border bg-beige text-foreground'
    }`}
  >
    <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
    <span>{message}</span>
  </div>
);

export const StarRating: React.FC<{ rating: number; count?: number }> = ({ rating, count }) => (
  <div className="inline-flex items-center gap-1 text-sm text-muted-fg">
    <Star className="h-4 w-4 fill-accent text-accent" aria-hidden="true" />
    <span className="font-semibold text-foreground">{rating.toFixed(1)}</span>
    {typeof count === 'number' && <span>({count})</span>}
  </div>
);
