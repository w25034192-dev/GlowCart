import React from 'react';
import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom';
import {
  BarChart3,
  Bell,
  Box,
  CalendarClock,
  CreditCard,
  FileSpreadsheet,
  FolderTree,
  LayoutDashboard,
  LogOut,
  MessageSquare,
  Package,
  Palette,
  Percent,
  Settings,
  ShoppingCart,
  Star,
  Tag,
  Users,
} from 'lucide-react';
import { useAuthStore } from '@/store/authStore';

const ADMIN_NAV = [
  { to: '/admin', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/admin/products', label: 'Products', icon: Package },
  { to: '/admin/categories', label: 'Categories', icon: FolderTree },
  { to: '/admin/brands', label: 'Brands', icon: Tag },
  { to: '/admin/variants', label: 'Variants', icon: Palette },
  { to: '/admin/inventory', label: 'Inventory', icon: Box },
  { to: '/admin/batches', label: 'Batches & Expiry', icon: CalendarClock },
  { to: '/admin/orders', label: 'Orders', icon: ShoppingCart },
  { to: '/admin/payments', label: 'Payments', icon: CreditCard },
  { to: '/admin/customers', label: 'Customers', icon: Users },
  { to: '/admin/promotions', label: 'Promotions', icon: Percent },
  { to: '/admin/coupons', label: 'Coupons', icon: Tag },
  { to: '/admin/reviews', label: 'Reviews', icon: Star },
  { to: '/admin/messages', label: 'Messages', icon: MessageSquare },
  { to: '/admin/notifications', label: 'Notifications', icon: Bell },
  { to: '/admin/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/admin/reports', label: 'Reports', icon: FileSpreadsheet },
  { to: '/admin/settings', label: 'Settings', icon: Settings },
];

export const AdminLayout: React.FC = () => {
  const { user, clearSession } = useAuthStore();
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen bg-background text-foreground">
      <aside className="hidden w-64 shrink-0 border-r border-border bg-card lg:flex lg:flex-col">
        <div className="flex items-center justify-between border-b border-border px-5 py-4">
          <Link to="/admin" className="font-serif text-2xl font-bold text-primary">
            GlowCart Admin
          </Link>
        </div>
        <nav aria-label="Admin sidebar" className="flex-1 space-y-1 overflow-y-auto p-3">
          {ADMIN_NAV.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  `touch-target flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-primary text-primary-fg'
                      : 'text-foreground hover:bg-muted'
                  }`
                }
              >
                <Icon className="h-4 w-4 shrink-0" aria-hidden="true" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
        <div className="border-t border-border p-4">
          <div className="mb-2 text-xs text-muted-fg">
            Signed in as <strong className="text-foreground">{user?.role}</strong>
          </div>
          <div className="flex gap-2">
            <Link
              to="/"
              className="touch-target flex-1 rounded-lg border border-border px-3 py-2 text-center text-xs font-medium hover:bg-muted"
            >
              Storefront
            </Link>
            <button
              type="button"
              onClick={() => {
                clearSession();
                navigate('/admin/login');
              }}
              aria-label="Sign out"
              className="touch-target inline-flex items-center justify-center rounded-lg border border-border px-3 py-2 text-xs hover:bg-muted"
            >
              <LogOut className="h-4 w-4" aria-hidden="true" />
            </button>
          </div>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-border bg-card px-4 py-3 lg:px-8">
          <div className="flex items-center gap-3">
            <span className="font-serif text-lg font-semibold lg:hidden">GlowCart Admin</span>
            <div className="flex flex-wrap gap-2 lg:hidden">
              <Link to="/admin" className="rounded bg-muted px-2 py-1 text-xs">Dashboard</Link>
              <Link to="/admin/products" className="rounded bg-muted px-2 py-1 text-xs">Products</Link>
              <Link to="/admin/inventory" className="rounded bg-muted px-2 py-1 text-xs">Inventory</Link>
              <Link to="/admin/orders" className="rounded bg-muted px-2 py-1 text-xs">Orders</Link>
            </div>
          </div>
          <span className="text-xs font-mono text-muted-fg">{user?.email}</span>
        </header>
        <main className="flex-1 p-4 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

