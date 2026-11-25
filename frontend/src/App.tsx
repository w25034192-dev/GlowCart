import React, { useEffect } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore } from '@/store/authStore';
import { useCartStore } from '@/store/cartStore';
import { CustomerLayout } from '@/layouts/CustomerLayout';
import { AdminLayout } from '@/layouts/AdminLayout';
import { ProtectedRoute } from '@/routes/ProtectedRoute';
import { HomePage } from '@/pages/customer/HomePage';
import { ForgotPasswordPage, LoginPage, RegisterPage } from '@/pages/customer/AuthPages';
import { CatalogPage } from '@/pages/customer/CatalogPage';
import { ProductDetailsPage } from '@/pages/customer/ProductDetailsPage';
import {
  CartPage,
  CheckoutPage,
  OrderConfirmationPage,
  PaymentResultPage,
  WishlistPage,
} from '@/pages/customer/CartWishlistCheckoutPages';
import {
  CustomerServicePage,
  NotificationsPage,
  OrderDetailsPage,
  OrderHistoryPage,
  ProfileAddressesPage,
} from '@/pages/customer/AccountOrdersSupportPages';
import {
  AboutPage,
  ContactPage,
  PrivacyPolicyPage,
  TermsPage,
} from '@/pages/customer/StaticInfoPages';
import { AdminLoginPage } from '@/pages/admin/AdminLoginPage';
import { AdminDashboardPage } from '@/pages/admin/AdminDashboardPage';
import {
  AdminBrandsPage,
  AdminCategoriesPage,
  AdminProductsPage,
  AdminVariantsPage,
} from '@/pages/admin/AdminCatalogPages';
import { AdminBatchesExpiryPage, AdminInventoryPage } from '@/pages/admin/AdminInventoryPages';
import {
  AdminCustomersPage,
  AdminMessagesPage,
  AdminNotificationsReportsSettingsPages,
  AdminOrdersPage,
  AdminPaymentsPage,
  AdminPromotionsCouponsPage,
  AdminReviewsPage,
} from '@/pages/admin/AdminOperationsPages';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 30_000, retry: 1 },
  },
});

export const AppRoutes: React.FC = () => {
  const { hydrate, user } = useAuthStore();
  const { fetchCart } = useCartStore();

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  useEffect(() => {
    if (user) {
      fetchCart();
    }
  }, [user, fetchCart]);

  return (
    <Routes>
      <Route element={<CustomerLayout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/catalog" element={<CatalogPage />} />
        <Route path="/products" element={<CatalogPage />} />
        <Route path="/category/:categorySlug" element={<CatalogPage />} />
        <Route path="/brand/:brandSlug" element={<CatalogPage />} />
        <Route path="/search" element={<CatalogPage />} />
        <Route path="/products/:id" element={<ProductDetailsPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/contact" element={<ContactPage />} />
        <Route path="/privacy" element={<PrivacyPolicyPage />} />
        <Route path="/terms" element={<TermsPage />} />

        <Route
          path="/cart"
          element={
            <ProtectedRoute>
              <CartPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/wishlist"
          element={
            <ProtectedRoute>
              <WishlistPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/checkout"
          element={
            <ProtectedRoute>
              <CheckoutPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/payment-result"
          element={
            <ProtectedRoute>
              <PaymentResultPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/order-confirmation/:orderId"
          element={
            <ProtectedRoute>
              <OrderConfirmationPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/orders"
          element={
            <ProtectedRoute>
              <OrderHistoryPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/orders/:orderId"
          element={
            <ProtectedRoute>
              <OrderDetailsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <ProfileAddressesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/support"
          element={
            <ProtectedRoute>
              <CustomerServicePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/notifications"
          element={
            <ProtectedRoute>
              <NotificationsPage />
            </ProtectedRoute>
          }
        />
      </Route>

      <Route path="/admin/login" element={<AdminLoginPage />} />
      <Route
        path="/admin"
        element={
          <ProtectedRoute allowedRoles={['admin', 'super_admin']} redirectTo="/admin/login">
            <AdminLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<AdminDashboardPage />} />
        <Route path="products" element={<AdminProductsPage />} />
        <Route path="categories" element={<AdminCategoriesPage />} />
        <Route path="brands" element={<AdminBrandsPage />} />
        <Route path="variants" element={<AdminVariantsPage />} />
        <Route path="inventory" element={<AdminInventoryPage />} />
        <Route path="batches" element={<AdminBatchesExpiryPage />} />
        <Route path="orders" element={<AdminOrdersPage />} />
        <Route path="payments" element={<AdminPaymentsPage />} />
        <Route path="customers" element={<AdminCustomersPage />} />
        <Route path="promotions" element={<AdminPromotionsCouponsPage />} />
        <Route path="coupons" element={<AdminPromotionsCouponsPage />} />
        <Route path="reviews" element={<AdminReviewsPage />} />
        <Route path="messages" element={<AdminMessagesPage />} />
        <Route
          path="notifications"
          element={<AdminNotificationsReportsSettingsPages.Notifications />}
        />
        <Route path="analytics" element={<AdminDashboardPage />} />
        <Route path="reports" element={<AdminNotificationsReportsSettingsPages.Reports />} />
        <Route path="settings" element={<AdminNotificationsReportsSettingsPages.Settings />} />
      </Route>
    </Routes>
  );
};

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;

