import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AppRoutes } from '@/App';
import { useAuthStore } from '@/store/authStore';

vi.mock('@/services/api', async () => {
  const actual = await vi.importActual<typeof import('@/services/api')>('@/services/api');
  return {
    ...actual,
    catalogApi: {
      getCategories: vi.fn().mockResolvedValue([
        { id: 'cat-1', name: 'Makeup', slug: 'makeup', is_active: true, sort_order: 1 },
      ]),
      getBrands: vi.fn().mockResolvedValue([
        { id: 'br-1', name: 'Rare Beauty', slug: 'rare-beauty', is_featured: true, is_active: true },
      ]),
      getProducts: vi.fn().mockResolvedValue({
        items: [
          {
            id: 'prod-1',
            name: 'Soft Pinch Liquid Blush',
            slug: 'soft-pinch-liquid-blush',
            category_id: 'cat-1',
            category_name: 'Makeup',
            brand_id: 'br-1',
            brand_name: 'Rare Beauty',
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
      }),
      getProduct: vi.fn().mockResolvedValue({
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
      }),
      getPromotions: vi.fn().mockResolvedValue([]),
    },
    engagementApi: {
      getProductReviews: vi.fn().mockResolvedValue([]),
      listMessages: vi.fn().mockResolvedValue([]),
      listNotifications: vi.fn().mockResolvedValue([]),
    },
  };
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
  it('renders storefront hero and navigation', async () => {
    useAuthStore.setState({ user: null, isLoading: false });
    renderAt('/');
    expect(await screen.findByText(/Curated Skincare, Shades/i)).toBeInTheDocument();
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
});

