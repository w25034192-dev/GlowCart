export function resolveMediaUrl(url?: string | null, fallbackText = 'GlowCart'): string {
  if (!url) {
    return `https://placehold.co/500x500/FAF8F6/1C1917?text=${encodeURIComponent(fallbackText)}`;
  }
  if (url.startsWith('/uploads/')) {
    const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
    const backendOrigin = apiBase.replace(/\/api\/v1\/?$/, '');
    return `${backendOrigin}${url}`;
  }
  return url;
}
