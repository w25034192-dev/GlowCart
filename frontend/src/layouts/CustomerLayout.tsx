import React, { useState } from 'react';
import { Link, Outlet, useNavigate } from 'react-router-dom';
import {
  Bell,
  Heart,
  Menu,
  Search,
  ShoppingBag,
  Sparkles,
  User as UserIcon,
  X,
} from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { useCartStore } from '@/store/cartStore';

export const CustomerLayout: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navigate = useNavigate();
  const { user, clearSession } = useAuthStore();
  const { itemCount, resetCart } = useCartStore();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    setMobileMenuOpen(false);
  };

  const handleLogout = () => {
    clearSession();
    resetCart();
    navigate('/');
  };

  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-primary focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-primary-fg"
      >
        Skip to main content
      </a>
      <div className="bg-beige px-4 py-1.5 text-center text-xs font-medium text-foreground">
        Free international demo shipping on orders over $75 USD · Code{' '}
        <span className="font-mono font-semibold text-rose">GLOW15</span> for 15% off
      </div>

      <header className="sticky top-0 z-30 border-b border-border bg-card/95 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setMobileMenuOpen((v) => !v)}
              aria-label="Toggle navigation menu"
              className="touch-target inline-flex items-center justify-center rounded-lg border border-border p-2 md:hidden"
            >
              {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
            <Link to="/" className="flex items-center gap-2 font-serif text-2xl font-bold text-primary">
              <Sparkles className="h-6 w-6" aria-hidden="true" />
              <span>GlowCart</span>
            </Link>
          </div>

          <form onSubmit={handleSearch} className="hidden flex-1 max-w-md md:flex">
            <label htmlFor="desktop-search" className="sr-only">
              Search cosmetics
            </label>
            <div className="relative w-full">
              <input
                id="desktop-search"
                type="search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search serums, lipsticks, brands..."
                className="w-full rounded-lg border border-border bg-background py-2.5 pl-4 pr-11 text-sm focus:border-primary focus:ring-2 focus:ring-ring/30"
              />
              <button
                type="submit"
                aria-label="Search products"
                className="touch-target absolute right-0 top-1/2 inline-flex -translate-y-1/2 items-center justify-center rounded-r-lg px-3 text-muted-fg hover:text-primary"
              >
                <Search className="h-4 w-4" aria-hidden="true" />
              </button>
            </div>
          </form>

          <nav aria-label="Customer actions" className="flex items-center gap-2">
            <Link
              to="/wishlist"
              aria-label="Wishlist"
              className="touch-target inline-flex items-center justify-center rounded-lg px-2.5 hover:bg-muted"
            >
              <Heart className="h-5 w-5" aria-hidden="true" />
            </Link>
            <Link
              to="/notifications"
              aria-label="Notifications"
              className="touch-target inline-flex items-center justify-center rounded-lg px-2.5 hover:bg-muted"
            >
              <Bell className="h-5 w-5" aria-hidden="true" />
            </Link>
            <Link
              to="/cart"
              aria-label="Shopping cart"
              className="touch-target relative inline-flex items-center justify-center rounded-lg px-2.5 hover:bg-muted"
            >
              <ShoppingBag className="h-5 w-5" aria-hidden="true" />
              {itemCount > 0 && (
                <span className="ml-1 rounded-full bg-primary px-1.5 py-0.5 font-mono text-xs font-semibold text-primary-fg">
                  {itemCount}
                </span>
              )}
            </Link>
            {user ? (
              <div className="hidden items-center gap-2 sm:flex">
                <Link
                  to="/profile"
                  className="touch-target inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-2 text-sm font-medium hover:bg-muted"
                >
                  <UserIcon className="h-4 w-4" aria-hidden="true" />
                  <span>{user.full_name?.split(' ')[0] || 'Account'}</span>
                </Link>
                {(user.role === 'admin' || user.role === 'super_admin') && (
                  <Link
                    to="/admin"
                    className="touch-target inline-flex items-center rounded-lg bg-secondary px-3 py-2 text-sm font-medium text-secondary-fg"
                  >
                    Admin
                  </Link>
                )}
                <button
                  type="button"
                  onClick={handleLogout}
                  className="touch-target rounded-lg px-3 py-2 text-sm text-muted-fg hover:text-foreground"
                >
                  Logout
                </button>
              </div>
            ) : (
              <Link
                to="/login"
                className="touch-target inline-flex items-center rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-fg"
              >
                Sign In
              </Link>
            )}
          </nav>
        </div>

        <nav
          aria-label="Main categories"
          className="hidden border-t border-border bg-card px-4 py-2 md:block"
        >
          <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-6 text-sm font-medium">
            <Link to="/catalog" className="hover:text-primary">
              All Products
            </Link>
            <Link to="/category/makeup" className="hover:text-primary">
              Makeup
            </Link>
            <Link to="/category/skincare" className="hover:text-primary">
              Skincare
            </Link>
            <Link to="/category/sun-care" className="hover:text-primary">
              Sun Care
            </Link>
            <Link to="/category/hair-care" className="hover:text-primary">
              Hair Care
            </Link>
            <Link to="/category/fragrance" className="hover:text-primary">
              Fragrance
            </Link>
            <Link to="/orders" className="hover:text-primary">
              Orders
            </Link>
            <Link to="/support" className="hover:text-primary">
              Support
            </Link>
          </div>
        </nav>

        {mobileMenuOpen && (
          <div className="border-t border-border bg-card p-4 md:hidden">
            <form onSubmit={handleSearch} className="mb-3 flex gap-2">
              <input
                type="search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search cosmetics..."
                className="flex-1 rounded-lg border border-border px-3 py-2 text-sm"
              />
              <button
                type="submit"
                className="touch-target rounded-lg bg-primary px-4 text-sm font-medium text-primary-fg"
              >
                Go
              </button>
            </form>
            <div className="flex flex-col gap-2 text-sm">
              <Link to="/catalog" onClick={() => setMobileMenuOpen(false)} className="py-1.5">
                All Products
              </Link>
              <Link to="/category/makeup" onClick={() => setMobileMenuOpen(false)} className="py-1.5">
                Makeup
              </Link>
              <Link to="/category/skincare" onClick={() => setMobileMenuOpen(false)} className="py-1.5">
                Skincare
              </Link>
              <Link to="/orders" onClick={() => setMobileMenuOpen(false)} className="py-1.5">
                Order History
              </Link>
              <Link to="/profile" onClick={() => setMobileMenuOpen(false)} className="py-1.5">
                Profile & Addresses
              </Link>
              <Link to="/support" onClick={() => setMobileMenuOpen(false)} className="py-1.5">
                Customer Service
              </Link>
            </div>
          </div>
        )}
      </header>

      <main id="main-content" className="mx-auto w-full max-w-7xl flex-1 px-4 py-8 sm:px-6">
        <Outlet />
      </main>

      <footer className="border-t border-border bg-beige/70 py-10">
        <div className="mx-auto grid max-w-7xl gap-8 px-4 sm:grid-cols-2 lg:grid-cols-4 sm:px-6">
          <div>
            <h3 className="font-serif text-xl font-bold text-primary">GlowCart</h3>
            <p className="mt-2 text-sm text-muted-fg">
              International cosmetic e-commerce & batch-aware inventory platform. Demo catalog
              prices are illustrative USD values.
            </p>
          </div>
          <div>
            <h4 className="text-sm font-semibold">Shop</h4>
            <ul className="mt-2 space-y-1.5 text-sm text-muted-fg">
              <li><Link to="/catalog" className="hover:text-primary">All Cosmetics</Link></li>
              <li><Link to="/category/makeup" className="hover:text-primary">Makeup</Link></li>
              <li><Link to="/category/skincare" className="hover:text-primary">Skincare</Link></li>
              <li><Link to="/category/sun-care" className="hover:text-primary">Sun Care</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold">Customer Care</h4>
            <ul className="mt-2 space-y-1.5 text-sm text-muted-fg">
              <li><Link to="/orders" className="hover:text-primary">Order Tracking</Link></li>
              <li><Link to="/support" className="hover:text-primary">Help & Messages</Link></li>
              <li><Link to="/about" className="hover:text-primary">About GlowCart</Link></li>
              <li><Link to="/contact" className="hover:text-primary">Contact</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold">Legal & Admin</h4>
            <ul className="mt-2 space-y-1.5 text-sm text-muted-fg">
              <li><Link to="/privacy" className="hover:text-primary">Privacy Policy</Link></li>
              <li><Link to="/terms" className="hover:text-primary">Terms & Conditions</Link></li>
              <li><Link to="/admin/login" className="hover:text-primary">Admin Portal</Link></li>
            </ul>
          </div>
        </div>
      </footer>
    </div>
  );
};

