import { BACKEND_ORIGIN } from '@/utils/apiConfig';

const REAL_COSMETIC_PHOTOGRAPHY: Record<string, string> = {
  // Foundations, cushions, concealers, powders
  foundation: 'https://images.unsplash.com/photo-1631729371254-42c2892f0e6e?auto=format&fit=crop&w=800&q=80',
  cushion: 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=800&q=80',
  concealer: 'https://images.unsplash.com/photo-1631729371254-42c2892f0e6e?auto=format&fit=crop&w=800&q=80',
  powder: 'https://images.unsplash.com/photo-1512496015851-a90fb38ba796?auto=format&fit=crop&w=800&q=80',
  // Lips, blushes & eyes
  lip: 'https://images.unsplash.com/photo-1586495777744-4413f21062fa?auto=format&fit=crop&w=800&q=80',
  lipstick: 'https://images.unsplash.com/photo-1586495777744-4413f21062fa?auto=format&fit=crop&w=800&q=80',
  gloss: 'https://images.unsplash.com/photo-1586495777744-4413f21062fa?auto=format&fit=crop&w=800&q=80',
  blush: 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=800&q=80',
  mascara: 'https://images.unsplash.com/photo-1516975080664-ed2fc6a32937?auto=format&fit=crop&w=800&q=80',
  // Skincare: Serums, ampoules, creams, toners, cleansers, thanakha
  serum: 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=800&q=80',
  ampoule: 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=800&q=80',
  snail: 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=800&q=80',
  cream: 'https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=800&q=80',
  moisturizer: 'https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=800&q=80',
  toner: 'https://images.unsplash.com/photo-1608248597359-00109f30325b?auto=format&fit=crop&w=800&q=80',
  essence: 'https://images.unsplash.com/photo-1608248597359-00109f30325b?auto=format&fit=crop&w=800&q=80',
  cleanser: 'https://images.unsplash.com/photo-1556228722-d0b5eb1c11d5?auto=format&fit=crop&w=800&q=80',
  thanakha: 'https://images.unsplash.com/photo-1571781926291-c477ebfd024b?auto=format&fit=crop&w=800&q=80',
  // Sun Care
  sun: 'https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?auto=format&fit=crop&w=800&q=80',
  uv: 'https://images.unsplash.com/photo-1567928815116-3e33b006c6e7?auto=format&fit=crop&w=800&q=80',
  spf: 'https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?auto=format&fit=crop&w=800&q=80',
  // Hair Care
  oil: 'https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?auto=format&fit=crop&w=800&q=80',
  shampoo: 'https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?auto=format&fit=crop&w=800&q=80',
  conditioner: 'https://images.unsplash.com/photo-1585751119414-ef2636f8aede?auto=format&fit=crop&w=800&q=80',
  // Body Care
  lotion: 'https://images.unsplash.com/photo-1616683693504-3ea7e9ad6fec?auto=format&fit=crop&w=800&q=80',
  butter: 'https://images.unsplash.com/photo-1556228722-d0b5eb1c11d5?auto=format&fit=crop&w=800&q=80',
  body: 'https://images.unsplash.com/photo-1616683693504-3ea7e9ad6fec?auto=format&fit=crop&w=800&q=80',
  // Fragrance
  perfume: 'https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?auto=format&fit=crop&w=800&q=80',
  mist: 'https://images.unsplash.com/photo-1547887537-6158d64c35b3?auto=format&fit=crop&w=800&q=80',
  fragrance: 'https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?auto=format&fit=crop&w=800&q=80',
  // Tools & Sets
  brush: 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=800&q=80',
  sponge: 'https://images.unsplash.com/photo-1512496015851-a90fb38ba796?auto=format&fit=crop&w=800&q=80',
  set: 'https://images.unsplash.com/photo-1608248597359-00109f30325b?auto=format&fit=crop&w=800&q=80',
  kit: 'https://images.unsplash.com/photo-1608248597359-00109f30325b?auto=format&fit=crop&w=800&q=80',
};

export function getRealFallbackImage(productName?: string, categoryName?: string): string {
  const query = `${productName || ''} ${categoryName || ''}`.toLowerCase();
  for (const [key, url] of Object.entries(REAL_COSMETIC_PHOTOGRAPHY)) {
    if (query.includes(key)) {
      return url;
    }
  }
  return 'https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=800&q=80';
}

export function resolveMediaUrl(
  url?: string | null,
  productName = 'GlowCart Cosmetic',
  categoryName?: string
): string {
  if (url && url.startsWith('/uploads/')) {
    return `${BACKEND_ORIGIN}${url}`;
  }
  if (url && !url.endsWith('.svg') && !url.includes('placehold.co')) {
    return url;
  }
  return getRealFallbackImage(productName, categoryName);
}
