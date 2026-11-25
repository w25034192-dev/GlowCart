import { BACKEND_ORIGIN } from '@/utils/apiConfig';

export function resolveMediaUrl(url?: string | null, fallbackText = 'GlowCart'): string {
  if (!url) {
    return `https://placehold.co/500x500/FAF8F6/1C1917?text=${encodeURIComponent(fallbackText)}`;
  }
  if (url.startsWith('/uploads/')) {
    return `${BACKEND_ORIGIN}${url}`;
  }
  return url;
}
