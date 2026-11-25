export type UserRole = 'customer' | 'admin' | 'super_admin';

export interface User {
  id: string;
  email: string;
  full_name: string;
  phone?: string | null;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface Address {
  id: string;
  label: string;
  recipient_name: string;
  phone: string;
  line1: string;
  line2?: string | null;
  city: string;
  state?: string | null;
  postal_code: string;
  country: string;
  is_default: boolean;
}

export interface Category {
  id: string;
  parent_id?: string | null;
  name: string;
  slug: string;
  description?: string | null;
  image_url?: string | null;
  is_active: boolean;
  sort_order: number;
}

export interface Brand {
  id: string;
  name: string;
  slug: string;
  description?: string | null;
  country_of_origin?: string | null;
  logo_url?: string | null;
  is_featured: boolean;
  is_active: boolean;
}

export interface ProductImage {
  id: string;
  image_url: string;
  alt_text?: string | null;
  is_primary: boolean;
  sort_order: number;
}

export interface ProductVariant {
  id: string;
  product_id: string;
  sku: string;
  shade_name?: string | null;
  shade_code?: string | null;
  color_name?: string | null;
  hex_color?: string | null;
  volume_ml?: number | null;
  weight_g?: string | null;
  size?: string | null;
  price: string;
  original_price?: string | null;
  is_available: boolean;
  status: string;
  available_quantity: number;
}

export interface ProductSummary {
  id: string;
  name: string;
  slug: string;
  short_description?: string | null;
  category_id: string;
  category_name: string;
  brand_id: string;
  brand_name: string;
  min_price?: string | null;
  max_price?: string | null;
  original_price?: string | null;
  primary_image_url?: string | null;
  average_rating: number;
  review_count: number;
  in_stock: boolean;
  is_featured: boolean;
  is_new_arrival: boolean;
  is_best_seller: boolean;
  is_demo: boolean;
  skin_types: string[];
}

export interface ProductDetail extends ProductSummary {
  description: string;
  specifications: Record<string, string>;
  verified_ingredients?: string | null;
  images: ProductImage[];
  variants: ProductVariant[];
  created_at: string;
}

export interface PaginatedProducts {
  items: ProductSummary[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface CartItem {
  id: string;
  variant_id: string;
  product_id: string;
  product_name: string;
  brand_name: string;
  sku: string;
  shade_name?: string | null;
  hex_color?: string | null;
  volume_ml?: number | null;
  size?: string | null;
  unit_price: string;
  quantity: number;
  line_total: string;
  available_quantity: number;
  image_url?: string | null;
}

export interface CartResponse {
  id: string;
  items: CartItem[];
  subtotal: string;
  discount_amount: string;
  shipping_fee: string;
  total_amount: string;
  coupon_code?: string | null;
  coupon_message?: string | null;
}

export interface WishlistResponse {
  id: string;
  items: Array<{
    id: string;
    product_id: string;
    product_name: string;
    slug: string;
    brand_name: string;
    min_price?: string | null;
    primary_image_url?: string | null;
  }>;
}

export type OrderStatus =
  | 'PENDING'
  | 'PAYMENT_PENDING'
  | 'PAID'
  | 'CONFIRMED'
  | 'PROCESSING'
  | 'SHIPPED'
  | 'DELIVERED'
  | 'CANCELLED'
  | 'REFUNDED';

export interface OrderItem {
  id: string;
  product_id?: string | null;
  variant_id?: string | null;
  product_name_snapshot: string;
  brand_name_snapshot?: string | null;
  category_name_snapshot?: string | null;
  variant_sku_snapshot: string;
  variant_label_snapshot: string;
  shade_name_snapshot?: string | null;
  volume_ml_snapshot?: number | null;
  unit_price: string;
  quantity: number;
  line_total: string;
}

export interface Order {
  id: string;
  order_number: string;
  user_id: string;
  status: OrderStatus;
  payment_method: 'COD' | 'SANDBOX';
  payment_status: string;
  currency: string;
  subtotal: string;
  discount_amount: string;
  shipping_fee: string;
  total_amount: string;
  coupon_code?: string | null;
  shipping_address_snapshot: Record<string, string | null>;
  notes?: string | null;
  tracking_number?: string | null;
  items: OrderItem[];
  created_at: string;
  updated_at: string;
}

export interface Review {
  id: string;
  product_id: string;
  user_id: string;
  author_name: string;
  rating: number;
  title?: string | null;
  comment: string;
  is_verified_purchase: boolean;
  is_approved: boolean;
  created_at: string;
}

export interface CustomerMessage {
  id: string;
  user_id: string;
  customer_email: string;
  subject: string;
  message: string;
  status: string;
  replies: Array<{
    id: string;
    sender_id: string;
    body: string;
    is_admin_reply: boolean;
    created_at: string;
  }>;
  created_at: string;
}

export interface NotificationItem {
  id: string;
  title: string;
  body: string;
  category: string;
  is_read: boolean;
  created_at: string;
}

export interface InventoryItem {
  variant_id: string;
  sku: string;
  product_name: string;
  variant_label: string;
  available_quantity: number;
  reserved_quantity: number;
  sellable_quantity: number;
  low_stock_threshold: number;
  is_low_stock: boolean;
  is_out_of_stock: boolean;
  updated_at: string;
}

export interface AnalyticsOverview {
  total_revenue: number;
  total_orders: number;
  total_customers: number;
  total_products: number;
  pending_orders: number;
  low_stock_products: number;
  out_of_stock_products: number;
  near_expiry_batches: number;
}

