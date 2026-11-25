import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AppRoutes } from '@/App';
import { catalogApi } from '@/services/api';
import { useAuthStore } from '@/store/authStore';

const ALL_CATEGORIES = [
  { id: 'cat-1', name: 'Makeup', slug: 'makeup', is_active: true, sort_order: 1 },
  { id: 'cat-2', name: 'Skincare', slug: 'skincare', is_active: true, sort_order: 2 },
  { id: 'cat-3', name: 'Sun Care', slug: 'sun-care', is_active: true, sort_order: 3 },
  { id: 'cat-4', name: 'Hair Care', slug: 'hair-care', is_active: true, sort_order: 4 },
  { id: 'cat-5', name: 'Body Care', slug: 'body-care', is_active: true, sort_order: 5 },
  { id: 'cat-6', name: 'Fragrance', slug: 'fragrance', is_active: true, sort_order: 6 },
  { id: 'cat-7', name: 'Beauty Tools', slug: 'beauty-tools', is_active: true, sort_order: 7 },
  { id: 'cat-8', name: 'Makeup Sets', slug: 'makeup-sets', is_active: true, sort_order: 8 },
];

const PRODUCTS_BY_CATEGORY: Record<string, { id: string; name: string; categoryName: string }> = {
  makeup: { id: 'prod-1', name: 'Soft Pinch Liquid Blush', categoryName: 'Makeup' },
  skincare: { id: 'prod-2', name: 'COSRX Advanced Snail 96 Mucin Essence', categoryName: 'Skincare' },
  'sun-care': { id: 'prod-3', name: 'Beauty of Joseon Relief Sun SPF50+', categoryName: 'Sun Care' },
  'hair-care': { id: 'prod-4', name: 'Olaplex No. 3 Hair Perfector', categoryName: 'Hair Care' },
  'body-care': { id: 'prod-5', name: 'Sol de Janeiro Brazilian Bum Bum Cream', categoryName: 'Body Care' },
  fragrance: { id: 'prod-6', name: 'Miss Dior Blooming Bouquet', categoryName: 'Fragrance' },
  'beauty-tools': { id: 'prod-7', name: 'Rare Beauty Liquid Blush Brush', categoryName: 'Beauty Tools' },
  'makeup-sets': { id: 'prod-8', name: 'COSRX Snail Glass Skin Starter Kit', categoryName: 'Makeup Sets' },
};

function makeProductResponse(params?: Record<string, unknown>) {
  const slug = String(params?.category_slug || 'makeup').toLowerCase();
  const q = String(params?.q || '').trim().toLowerCase();
  const entry = PRODUCTS_BY_CATEGORY[slug] || PRODUCTS_BY_CATEGORY.makeup;

  if (q && !entry.name.toLowerCase().includes(q)) {
    return { items: [], total: 0, page: 1, page_size: 12, total_pages: 1 };
  }

  return {
    items: [
      {
        id: entry.id,
        name: entry.name,
        slug: entry.name.toLowerCase().replace(/[^a-z0-9]+/g, '-'),
        category_id: 'cat-match',
        category_name: entry.categoryName,
        brand_id: 'br-1',
        brand_name: 'GlowCart Demo',
        min_price: '23.00',
        max_price: '23.00',
        average_rating: 4.8,
        review_count: 2,
        in_stock: true,
        is_featured: true,
        is_new_arrival: true,
        is_best_seller: true,
        is_demo: true,
        skin_types: ['all'],
      },
    ],
    total: 1,
    page: 1,
    page_size: 12,
    total_pages: 1,
  };
}

vi.mock('@/services/api', async () => {
  const actual = await vi.importActual<typeof import('@/services/api')>('@/services/api');
  return {
    ...actual,
    catalogApi: {
      getCategories: vi.fn(),
      getBrands: vi.fn(),
      getProducts: vi.fn(),
      getProduct: vi.fn(),
      getPromotions: vi.fn(),
    },
    engagementApi: {
      getProductReviews: vi.fn().mockResolvedValue([]),
      listMessages: vi.fn().mockResolvedValue([]),
      listNotifications: vi.fn().mockResolvedValue([]),
    },
  };
});

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(catalogApi.getCategories).mockResolvedValue(ALL_CATEGORIES);
  vi.mocked(catalogApi.getBrands).mockResolvedValue([
    { id: 'br-1', name: 'Rare Beauty', slug: 'rare-beauty', is_featured: true, is_active: true },
  ]);
  vi.mocked(catalogApi.getProducts).mockImplementation(async (params) =>
    makeProductResponse(params as Record<string, unknown>)
  );
  vi.mocked(catalogApi.getProduct).mockResolvedValue({
    id: 'prod-1',
    name: 'Soft Pinch Liquid Blush',
    slug: 'soft-pinch-liquid-blush',
    description: 'Weightless liquid blush.',
    category_id: 'cat-1',
    category_name: 'Makeup',
    brand_id: 'br-1',
    brand_name: 'Rare Beauty',
    min_price: '23.00',
    max_price: '25.00',
    average_rating: 4.8,
    review_count: 1,
    in_stock: true,
    is_featured: true,
    is_new_arrival: true,
    is_best_seller: true,
    is_demo: true,
    skin_types: ['all'],
    specifications: {},
    images: [],
    variants: [
      {
        id: 'var-1',
        product_id: 'prod-1',
        sku: 'RB-JOY',
        shade_name: 'Joy',
        hex_color: '#E47A68',
        price: '23.00',
        is_available: true,
        status: 'ACTIVE',
        available_quantity: 8,
      },
      {
        id: 'var-2',
        product_id: 'prod-1',
        sku: 'RB-HOPE',
        shade_name: 'Hope',
        hex_color: '#C97A7E',
        price: '25.00',
        is_available: true,
        status: 'ACTIVE',
        available_quantity: 4,
      },
    ],
    created_at: new Date().toISOString(),
  });
  vi.mocked(catalogApi.getPromotions).mockResolvedValue([]);
});

function renderAt(path: string) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={[path]}>
        <AppRoutes />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe('GlowCart Frontend', () => {
  it('renders storefront hero, featured categories, best sellers, routine builder, and testimonials', async () => {
    useAuthStore.setState({ user: null, isLoading: false });
    const user = userEvent.setup();
    renderAt('/');
    expect(await screen.findByText(/Curated Skincare, Shades/i)).toBeInTheDocument();
    expect(await screen.findByText(/Featured Categories/i)).toBeInTheDocument();
    expect(await screen.findByText(/Best Sellers/i)).toBeInTheDocument();
    expect(screen.getByText(/Build Your Skin-Type Routine/i)).toBeInTheDocument();
    expect(screen.getByText(/Customer Testimonials/i)).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: 'Sensitive' }));
    expect(screen.getByRole('link', { name: /Shop Sensitive Skin Formulas/i })).toHaveAttribute(
      'href',
      '/catalog?skin_type=sensitive'
    );
  });

  it('redirects unauthenticated visitors away from protected admin routes', async () => {
    useAuthStore.setState({ user: null, isLoading: false });
    renderAt('/admin');
    expect(await screen.findByText(/GlowCart Admin/i)).toBeInTheDocument();
  });

  it('updates SKU and price when selecting product shade variant', async () => {
    useAuthStore.setState({ user: null, isLoading: false });
    const user = userEvent.setup();
    renderAt('/products/prod-1');
    expect(await screen.findByText(/SKU: RB-JOY/i)).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /Hope/i }));
    expect(await screen.findByText(/SKU: RB-HOPE/i)).toBeInTheDocument();
    expect(screen.getByText('$25.00')).toBeInTheDocument();
  });

  it('loads skincare products and resets stale keyword filters when navigating between categories', async () => {
    useAuthStore.setState({ user: null, isLoading: false });
    const user = userEvent.setup();
    renderAt('/category/makeup');

    expect(await screen.findByText('Soft Pinch Liquid Blush')).toBeInTheDocument();
    expect(screen.getByText('1 products available')).toBeInTheDocument();

    // Filter on Makeup page so keyword would exclude Skincare if carried across routes
    const searchInput = screen.getByLabelText('Keyword');
    await user.type(searchInput, 'Blush');

    // Navigate via navbar link to Skincare
    await user.click(screen.getAllByRole('link', { name: 'Skincare' })[0]);

    expect(await screen.findByText('COSRX Advanced Snail 96 Mucin Essence')).toBeInTheDocument();
    expect(screen.getByText('1 products available')).toBeInTheDocument();
    await waitFor(() => {
      expect(catalogApi.getProducts).toHaveBeenLastCalledWith(
        expect.objectContaining({
          category_slug: 'skincare',
          q: undefined,
          page: 1,
        })
      );
    });
  });

  it('renders products cleanly across all seeded category pages', async () => {
    useAuthStore.setState({ user: null, isLoading: false });
    for (const cat of ALL_CATEGORIES) {
      const { unmount } = renderAt(`/category/${cat.slug}`);
      const expectedProduct = PRODUCTS_BY_CATEGORY[cat.slug].name;
      expect(await screen.findByText(expectedProduct)).toBeInTheDocument();
      expect(screen.getByText('1 products available')).toBeInTheDocument();
      expect(catalogApi.getProducts).toHaveBeenCalledWith(
        expect.objectContaining({ category_slug: cat.slug, page: 1 })
      );
      unmount();
    }
  });

  it('shows an error alert with retry instead of 0 products when catalog API fails', async () => {
    useAuthStore.setState({ user: null, isLoading: false });
    vi.mocked(catalogApi.getProducts).mockRejectedValueOnce(new Error('Network error'));
    renderAt('/category/skincare');

    expect(await screen.findByRole('alert')).toHaveTextContent(/Unable to load products/i);
    expect(screen.queryByText('0 products available')).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Retry/i })).toBeInTheDocument();
  });
});


