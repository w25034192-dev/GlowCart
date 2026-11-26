import React, { useState } from 'react';
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
  Menu,
  MessageSquare,
  Package,
  Palette,
  Percent,
  Settings,
  ShoppingCart,
  Star,
  Tag,
  Users,
  X,
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
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  const handleSignOut = () => {
    clearSession();
    navigate('/admin/login');
  };

  const renderNavItems = (onNavigate?: () => void) =>
    ADMIN_NAV.map((item) => {
      const Icon = item.icon;
      return (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.end}
          onClick={onNavigate}
          className={({ isActive }) =>
            `touch-target flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
              isActive
                ? 'bg-plum text-white shadow-sm'
                : 'text-foreground hover:bg-blush-soft hover:text-plum'
            }`
          }
        >
          <Icon className="h-4 w-4 shrink-0" aria-hidden="true" />
          <span>{item.label}</span>
        </NavLink>
      );
    });

  return (
    <div className="flex min-h-screen bg-cream-warm text-foreground">
      {/* Desktop Sidebar */}
      <aside className="hidden w-64 shrink-0 border-r border-border bg-card lg:flex lg:flex-col">
        <div className="flex items-center justify-between border-b border-border px-5 py-4">
          <Link to="/admin" className="font-serif text-2xl font-bold text-plum">
            GlowCart Admin
          </Link>
        </div>
        <nav aria-label="Admin sidebar" className="flex-1 space-y-1 overflow-y-auto p-3">
          {renderNavItems()}
        </nav>
        <div className="border-t border-border p-4">
          <div className="mb-2 text-xs text-muted-fg">
            Signed in as <strong className="text-plum">{user?.role}</strong>
          </div>
          <div className="flex gap-2">
            <Link
              to="/"
              className="touch-target flex-1 rounded-lg border border-border px-3 py-2 text-center text-xs font-medium hover:bg-blush-soft"
            >
              Storefront
            </Link>
            <button
              type="button"
              onClick={handleSignOut}
              aria-label="Sign out"
              className="touch-target inline-flex items-center justify-center rounded-lg border border-border px-3 py-2 text-xs hover:bg-blush-soft"
            >
              <LogOut className="h-4 w-4" aria-hidden="true" />
            </button>
          </div>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 flex items-center justify-between border-b border-border bg-card/95 px-4 py-3 backdrop-blur-md lg:px-8">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setMobileNavOpen((v) => !v)}
              aria-label="Toggle admin navigation"
              aria-expanded={mobileNavOpen}
              className="touch-target inline-flex items-center justify-center rounded-lg border border-border bg-card p-2 text-plum hover:bg-blush-soft lg:hidden"
            >
              {mobileNavOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
            <span className="font-serif text-lg font-bold text-plum lg:hidden">GlowCart Admin</span>
          </div>
          <span className="truncate font-mono text-xs text-muted-fg">{user?.email}</span>
        </header>

        {/* Mobile Full Admin Navigation Drawer */}
        {mobileNavOpen && (
          <div className="border-b border-border bg-card p-4 shadow-lg lg:hidden">
            <nav aria-label="Mobile admin navigation" className="grid grid-cols-2 gap-1.5 sm:grid-cols-3">
              {renderNavItems(() => setMobileNavOpen(false))}
            </nav>
            <div className="mt-4 flex items-center justify-between gap-2 border-t border-border pt-3">
              <Link
                to="/"
                onClick={() => setMobileNavOpen(false)}
                className="touch-target flex-1 rounded-lg border border-border px-3 py-2 text-center text-xs font-semibold hover:bg-blush-soft"
              >
                Back to Storefront
              </Link>
              <button
                type="button"
                onClick={handleSignOut}
                className="touch-target inline-flex items-center gap-1.5 rounded-lg bg-plum px-4 py-2 text-xs font-semibold text-white"
              >
                <LogOut className="h-3.5 w-3.5" aria-hidden="true" />
                <span>Sign Out</span>
              </button>
            </div>
          </div>
        )}

        <main className="flex-1 p-4 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
