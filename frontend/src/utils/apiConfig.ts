declare global {
  interface Window {
    __GLOWCART_CONFIG__?: {
      VITE_API_BASE_URL?: string;
    };
  }
}

const DEFAULT_API_BASE_URL = 'http://localhost:8000/api/v1';

export function resolveApiBaseUrl(
  rawBuildUrl: string | undefined = import.meta.env.VITE_API_BASE_URL,
  pageProtocol: string = typeof window !== 'undefined' ? window.location.protocol : 'http:',
  rawRuntimeUrl: string | undefined =
    typeof window !== 'undefined' ? window.__GLOWCART_CONFIG__?.VITE_API_BASE_URL : undefined
): string {
  const candidate = (
    rawRuntimeUrl?.trim() ||
    rawBuildUrl?.trim() ||
    DEFAULT_API_BASE_URL
  )
    .trim()
    .replace(/^['"]+|['"]+$/g, '');

  let normalized = candidate || DEFAULT_API_BASE_URL;
  if (!/^https?:\/\//i.test(normalized)) {
    const isLocal = /^(localhost|127\.0\.0\.1)(:|\/|$)/i.test(normalized);
    normalized = `${isLocal ? 'http' : 'https'}://${normalized}`;
  }

  if (
    pageProtocol === 'https:' &&
    /^http:\/\//i.test(normalized) &&
    !/^http:\/\/(localhost|127\.0\.0\.1)(:|\/|$)/i.test(normalized)
  ) {
    normalized = normalized.replace(/^http:\/\//i, 'https://');
  }

  normalized = normalized.replace(/\/+$/, '').replace(/(\/api\/v1)+$/i, '/api/v1');
  if (!/\/api\/v1$/i.test(normalized)) {
    normalized = `${normalized}/api/v1`;
  }

  return normalized;
}

export const API_BASE_URL = resolveApiBaseUrl();
export const BACKEND_ORIGIN = API_BASE_URL.replace(/\/api\/v1$/i, '');
