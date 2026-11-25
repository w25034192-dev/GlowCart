import axios from 'axios';
import { API_BASE_URL } from '@/utils/apiConfig';
import type {
  Address,
  AnalyticsOverview,
  Brand,
  CartResponse,
  Category,
  CustomerMessage,
  InventoryItem,
  NotificationItem,
  Order,
  PaginatedProducts,
  ProductDetail,
  Review,
  User,
  WishlistResponse,
} from '@/types';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('glowcart_access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original?._retry) {
      const refreshToken = localStorage.getItem('glowcart_refresh_token');
      if (refreshToken) {
        original._retry = true;
        try {
          const { data } = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          localStorage.setItem('glowcart_access_token', data.access_token);
          localStorage.setItem('glowcart_refresh_token', data.refresh_token);
          original.headers.Authorization = `Bearer ${data.access_token}`;
          return apiClient(original);
        } catch {
          localStorage.removeItem('glowcart_access_token');
          localStorage.removeItem('glowcart_refresh_token');
        }
      }
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  register: (payload: { email: string; full_name: string; password: string; phone?: string }) =>
    apiClient.post<User>('/auth/register', payload).then((r) => r.data),
  login: (payload: { email: string; password: string }) =>
    apiClient
      .post<{ access_token: string; refresh_token: string; user: User }>('/auth/login', payload)
      .then((r) => r.data),
  logout: (refresh_token?: string | null) =>
    apiClient.post('/auth/logout', { refresh_token }).then((r) => r.data),
  me: () => apiClient.get<User>('/auth/me').then((r) => r.data),
  updateProfile: (payload: { full_name?: string; phone?: string }) =>
    apiClient.put<User>('/auth/me', payload).then((r) => r.data),
  forgotPassword: (email: string) =>
    apiClient.post<{ message: string; reset_token?: string }>('/auth/forgot-password', { email }).then((r) => r.data),
  resetPassword: (payload: { token: string; new_password: string }) =>
    apiClient.post('/auth/reset-password', payload).then((r) => r.data),
  listAddresses: () => apiClient.get<Address[]>('/addresses').then((r) => r.data),
  createAddress: (payload: Omit<Address, 'id'>) =>
    apiClient.post<Address>('/addresses', payload).then((r) => r.data),
  deleteAddress: (id: string) => apiClient.delete(`/addresses/${id}`),
};

export const catalogApi = {
  getCategories: () => apiClient.get<Category[]>('/categories').then((r) => r.data),
  getBrands: () => apiClient.get<Brand[]>('/brands').then((r) => r.data),
  getProducts: (params: Record<string, string | number | boolean | undefined>) =>
    apiClient.get<PaginatedProducts>('/products', { params }).then((r) => r.data),
  searchProducts: (q: string, page = 1) =>
    apiClient
      .get<PaginatedProducts>('/products/search', { params: { q, page } })
      .then((r) => r.data),
  getProduct: (id: string) =>
    apiClient.get<ProductDetail>(`/products/${id}`).then((r) => r.data),
  getPromotions: () => apiClient.get('/promotions').then((r) => r.data),
};

export const cartApi = {
  getCart: (couponCode?: string) =>
    apiClient
      .get<CartResponse>('/cart', {
        params: couponCode ? { coupon_code: couponCode } : undefined,
      })
      .then((r) => r.data),
  addItem: (variant_id: string, quantity = 1) =>
    apiClient.post<CartResponse>('/cart/items', { variant_id, quantity }).then((r) => r.data),
  updateItem: (itemId: string, quantity: number) =>
    apiClient.put<CartResponse>(`/cart/items/${itemId}`, { quantity }).then((r) => r.data),
  removeItem: (itemId: string) =>
    apiClient.delete<CartResponse>(`/cart/items/${itemId}`).then((r) => r.data),
  getWishlist: () => apiClient.get<WishlistResponse>('/wishlist').then((r) => r.data),
  addWishlist: (product_id: string) =>
    apiClient.post<WishlistResponse>('/wishlist/items', { product_id }).then((r) => r.data),
  removeWishlist: (itemId: string) =>
    apiClient.delete<WishlistResponse>(`/wishlist/items/${itemId}`).then((r) => r.data),
};

export const orderApi = {
  createOrder: (payload: {
    address_id: string;
    payment_method: 'COD' | 'SANDBOX';
    coupon_code?: string;
    idempotency_key: string;
    notes?: string;
  }) => apiClient.post<Order>('/orders', payload).then((r) => r.data),
  listOrders: () => apiClient.get<Order[]>('/orders').then((r) => r.data),
  getOrder: (id: string) => apiClient.get<Order>(`/orders/${id}`).then((r) => r.data),
  cancelOrder: (id: string) => apiClient.post<Order>(`/orders/${id}/cancel`).then((r) => r.data),
  initiatePayment: (order_id: string) =>
    apiClient.post('/payments', { order_id }).then((r) => r.data),
};

export const engagementApi = {
  getProductReviews: (productId: string) =>
    apiClient.get<Review[]>(`/products/${productId}/reviews`).then((r) => r.data),
  createReview: (payload: { product_id: string; rating: number; title?: string; comment: string }) =>
    apiClient.post<Review>('/reviews', payload).then((r) => r.data),
  deleteReview: (reviewId: string) => apiClient.delete(`/reviews/${reviewId}`),
  listMessages: () => apiClient.get<CustomerMessage[]>('/messages').then((r) => r.data),
  createMessage: (payload: { subject: string; message: string }) =>
    apiClient.post<CustomerMessage>('/messages', payload).then((r) => r.data),
  listNotifications: () =>
    apiClient.get<NotificationItem[]>('/notifications').then((r) => r.data),
  markRead: (id: string) =>
    apiClient.patch<NotificationItem>(`/notifications/${id}/read`).then((r) => r.data),
};

export const adminApi = {
  getOverview: () =>
    apiClient.get<AnalyticsOverview>('/admin/analytics/overview').then((r) => r.data),
  getSalesSeries: (granularity = 'daily') =>
    apiClient
      .get<Array<{ period: string; revenue: number; orders: number }>>('/admin/analytics/sales', {
        params: { granularity },
      })
      .then((r) => r.data),
  getBestSellers: () =>
    apiClient
      .get<Array<{ product_name: string; units_sold: number; revenue: number }>>(
        '/admin/analytics/best-sellers'
      )
      .then((r) => r.data),
  getCategorySales: () =>
    apiClient
      .get<{
        by_category: Array<{ name: string; revenue: number }>;
        by_brand: Array<{ name: string; revenue: number }>;
      }>('/admin/analytics/categories')
      .then((r) => r.data),
  getVariantAnalytics: () =>
    apiClient
      .get<{
        lipstick_shades: Array<{ shade: string; units_sold: number }>;
        foundation_shades: Array<{ shade: string; units_sold: number }>;
        by_color: Array<{ color: string; units_sold: number }>;
        by_volume: Array<{ volume: string; units_sold: number }>;
      }>('/admin/analytics/variants')
      .then((r) => r.data),
  getInventoryAnalytics: () => apiClient.get('/admin/analytics/inventory').then((r) => r.data),
  getInventory: () => apiClient.get<InventoryItem[]>('/admin/inventory').then((r) => r.data),
  getExpiring: () => apiClient.get('/admin/inventory/expiring').then((r) => r.data),
  adjustInventory: (payload: { variant_id: string; quantity_delta: number; reason: string }) =>
    apiClient.post('/admin/inventory/adjustments', payload).then((r) => r.data),
  receiveBatch: (payload: {
    variant_id: string;
    batch_number: string;
    manufacture_date: string;
    expiry_date: string;
    quantity: number;
  }) => apiClient.post('/admin/inventory/batches', payload).then((r) => r.data),
  getOrders: () => apiClient.get<Order[]>('/admin/orders').then((r) => r.data),
  updateOrderStatus: (id: string, status: string, tracking_number?: string) =>
    apiClient.patch<Order>(`/admin/orders/${id}/status`, { status, tracking_number }).then((r) => r.data),
  getPayments: () => apiClient.get('/admin/payments').then((r) => r.data),
  refundPayment: (id: string, reason: string) =>
    apiClient.post(`/admin/payments/${id}/refund`, { reason }).then((r) => r.data),
  getCustomers: () => apiClient.get<User[]>('/admin/customers').then((r) => r.data),
  getReviews: () => apiClient.get<Review[]>('/admin/reviews').then((r) => r.data),
  moderateReview: (id: string, is_approved: boolean) =>
    apiClient.patch(`/admin/reviews/${id}/moderate`, { is_approved }).then((r) => r.data),
  replyMessage: (id: string, body: string, status = 'RESOLVED') =>
    apiClient.post(`/admin/messages/${id}/reply`, { body, status }).then((r) => r.data),
  getCoupons: () => apiClient.get('/admin/coupons').then((r) => r.data),
  getAuditLogs: () => apiClient.get('/admin/audit-logs').then((r) => r.data),
  getSettings: () => apiClient.get('/admin/settings').then((r) => r.data),
  updateSettings: (payload: Record<string, unknown>) =>
    apiClient.put('/admin/settings', payload).then((r) => r.data),
  createProduct: (payload: Record<string, unknown>) =>
    apiClient.post('/admin/products', payload).then((r) => r.data),
  createCategory: (payload: Record<string, unknown>) =>
    apiClient.post('/admin/categories', payload).then((r) => r.data),
  createBrand: (payload: Record<string, unknown>) =>
    apiClient.post('/admin/brands', payload).then((r) => r.data),
  createVariant: (payload: Record<string, unknown>) =>
    apiClient.post('/admin/variants', payload).then((r) => r.data),
  createPromotion: (payload: Record<string, unknown>) =>
    apiClient.post('/admin/promotions', payload).then((r) => r.data),
  createAdminUser: (payload: Record<string, unknown>) =>
    apiClient.post('/admin/users', payload).then((r) => r.data),
};

