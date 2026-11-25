/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        background: 'var(--color-background)',
        card: 'var(--color-card)',
        muted: 'var(--color-muted)',
        foreground: 'var(--color-foreground)',
        'card-fg': 'var(--color-card-foreground)',
        'muted-fg': 'var(--color-muted-foreground)',
        primary: 'var(--color-primary)',
        'primary-fg': 'var(--color-on-primary)',
        secondary: 'var(--color-secondary)',
        'secondary-fg': 'var(--color-on-secondary)',
        accent: 'var(--color-accent)',
        'accent-fg': 'var(--color-on-accent)',
        border: 'var(--color-border)',
        destructive: 'var(--color-destructive)',
        'destructive-fg': 'var(--color-on-destructive)',
        ring: 'var(--color-ring)',
        blush: 'var(--color-blush)',
        beige: 'var(--color-beige)',
        rose: 'var(--color-rose)',
      },
      fontFamily: {
        sans: ['Montserrat', 'system-ui', '-apple-system', 'sans-serif'],
        serif: ['Cormorant', 'Georgia', 'serif'],
        mono: ['"Fira Code"', 'ui-monospace', 'monospace'],
      },
    },
  },
  plugins: [],
};
