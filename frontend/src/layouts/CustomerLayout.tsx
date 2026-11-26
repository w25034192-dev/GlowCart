import React, { useState } from 'react';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import {
  ArrowUp,
  Award,
  Bell,
  Check,
  Copy,
  Heart,
  Menu,
  RotateCcw,
  Search,
  ShieldCheck,
  ShoppingBag,
  Sparkles,
  Truck,
  User as UserIcon,
  X,
} from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { useCartStore } from '@/store/cartStore';
import { AtelierBagToast } from '@/components/customer/AtelierBagToast';

export const CustomerLayout: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [copiedCode, setCopiedCode] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, clearSession } = useAuthStore();
  const { itemCount, resetCart } = useCartStore();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
      setMobileMenuOpen(false);
    }
  };

  const handleCopyCode = () => {
    navigator.clipboard?.writeText('GLOW15');
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  };

  const handleLogout = () => {
    clearSession();
    resetCart();
    navigate('/');
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground selection:bg-blush selection:text-primary">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-primary focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-primary-fg shadow-lg"
      >
        Skip to main content
      </a>

      {/* Top Editorial Announcement Banner */}
      <div className="relative z-40 border-b border-border/60 bg-gradient-to-r from-beige via-blush/60 to-beige px-4 py-2 text-center text-xs font-medium text-foreground">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <span className="hidden items-center gap-1.5 text-muted-fg sm:inline-flex">
            <Sparkles className="h-3.5 w-3.5 text-accent" aria-hidden="true" />
            <span>Curated Clean &amp; Luxury Beauty Atelier</span>
          </span>

          <div className="flex flex-1 items-center justify-center gap-2 sm:flex-initial">
            <span>Free international delivery on orders over $75 USD</span>
            <span className="text-muted-fg">·</span>
            <button
              type="button"
              onClick={handleCopyCode}
              title="Click to copy 15% discount code"
              className="inline-flex cursor-pointer items-center gap-1 rounded-full border border-rose/30 bg-card/80 px-2.5 py-0.5 font-mono text-[11px] font-semibold text-rose transition-colors hover:bg-card"
            >
              <span>GLOW15</span>
              {copiedCode ? (
                <Check className="h-3 w-3 text-emerald-600" />
              ) : (
                <Copy className="h-3 w-3 opacity-60" />
              )}
            </button>
            <span className="hidden text-[11px] text-muted-fg lg:inline">(15% off)</span>
          </div>

          <span className="hidden items-center gap-2 font-mono text-[11px] text-muted-fg sm:inline-flex">
            <span>Freshness FEFO Batch Verified</span>
          </span>
        </div>
      </div>

      {/* Main Luxury Sticky Header */}
      <header className="sticky top-0 z-30 border-b border-border/80 bg-card/90 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3.5 sm:px-6">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setMobileMenuOpen((v) => !v)}
              aria-label="Toggle navigation menu"
              className="touch-target inline-flex items-center justify-center rounded-xl border border-border/80 bg-card/60 p-2 transition-colors hover:bg-muted md:hidden"
            >
              {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>

            <Link to="/" className="group flex items-center gap-2.5">
              <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-fg shadow-sm transition-transform duration-300 group-hover:scale-105">
                <Sparkles className="h-5 w-5 text-amber-300" aria-hidden="true" />
              </span>
              <div className="flex flex-col">
                <span className="font-serif text-2xl font-bold tracking-tight text-foreground transition-colors group-hover:text-primary">
                  GlowCart
                </span>
                <span className="hidden text-[9px] font-semibold uppercase tracking-[0.2em] text-muted-fg sm:block">
                  Atelier de Beauté
                </span>
              </div>
            </Link>
          </div>

          {/* Search Bar with Luxury Polish */}
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
                placeholder="Search serums, shades, Thanakha, sun sticks..."
                className="w-full rounded-full border border-border/80 bg-background/80 py-2.5 pl-4 pr-11 text-sm shadow-inner transition-all duration-200 focus:border-primary focus:bg-card focus:shadow-sm focus:ring-2 focus:ring-ring/20"
              />
              <button
                type="submit"
                aria-label="Search products"
                className="touch-target absolute right-0 top-1/2 inline-flex -translate-y-1/2 items-center justify-center rounded-r-full px-3.5 text-muted-fg transition-colors hover:text-primary"
              >
                <Search className="h-4 w-4" aria-hidden="true" />
              </button>
            </div>
          </form>

          {/* Customer Action Bar */}
          <nav aria-label="Customer actions" className="flex items-center gap-1.5 sm:gap-2">
            <Link
              to="/wishlist"
              aria-label="Wishlist"
              className="touch-target inline-flex items-center justify-center rounded-xl border border-transparent p-2 text-foreground transition-colors hover:border-border hover:bg-muted/70"
            >
              <Heart className="h-5 w-5" aria-hidden="true" />
            </Link>

            <Link
              to="/notifications"
              aria-label="Notifications"
              className="touch-target inline-flex items-center justify-center rounded-xl border border-transparent p-2 text-foreground transition-colors hover:border-border hover:bg-muted/70"
            >
              <Bell className="h-5 w-5" aria-hidden="true" />
            </Link>

            <Link
              to="/cart"
              aria-label="Shopping cart"
              className="touch-target relative inline-flex items-center justify-center rounded-xl border border-transparent p-2 text-foreground transition-colors hover:border-border hover:bg-muted/70"
            >
              <ShoppingBag className="h-5 w-5" aria-hidden="true" />
              {itemCount > 0 && (
                <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-primary font-mono text-[11px] font-bold text-primary-fg shadow-sm animate-pulse">
                  {itemCount}
                </span>
              )}
            </Link>

            {user ? (
              <div className="hidden items-center gap-2 sm:flex">
                <Link
                  to="/profile"
                  className="touch-target inline-flex items-center gap-2 rounded-xl border border-border/80 bg-card px-3.5 py-2 text-sm font-medium transition-colors hover:bg-muted"
                >
                  <UserIcon className="h-4 w-4 text-accent" aria-hidden="true" />
                  <span>{user.full_name?.split(' ')[0] || 'Account'}</span>
                </Link>
                {(user.role === 'admin' || user.role === 'super_admin') && (
                  <Link
                    to="/admin"
                    className="touch-target inline-flex items-center rounded-xl bg-secondary px-3.5 py-2 text-sm font-medium text-secondary-fg shadow-sm transition-opacity hover:opacity-90"
                  >
                    Admin
                  </Link>
                )}
                <button
                  type="button"
                  onClick={handleLogout}
                  className="touch-target rounded-xl px-3 py-2 text-sm text-muted-fg transition-colors hover:text-foreground"
                >
                  Logout
                </button>
              </div>
            ) : (
              <Link
                to="/login"
                className="touch-target inline-flex items-center rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-primary-fg shadow-sm transition-opacity hover:opacity-90"
              >
                Sign In
              </Link>
            )}
          </nav>
        </div>

        {/* Category & Experience Sub-Navigation Bar */}
        <nav
          aria-label="Main categories"
          className="hidden border-t border-border/60 bg-card/60 px-4 py-2.5 backdrop-blur-sm md:block"
        >
          <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 text-xs font-medium">
            <div className="flex flex-wrap items-center gap-5">
              <Link
                to="/catalog"
                className={`transition-colors hover:text-primary ${
                  location.pathname === '/catalog' && !location.search
                    ? 'font-bold text-primary underline underline-offset-8'
                    : 'text-muted-fg'
                }`}
              >
                All Products
              </Link>
              <Link
                to="/category/makeup"
                className={`transition-colors hover:text-primary ${
                  location.pathname.includes('/makeup')
                    ? 'font-bold text-primary underline underline-offset-8'
                    : 'text-muted-fg'
                }`}
              >
                Makeup
              </Link>
              <Link
                to="/category/skincare"
                className={`transition-colors hover:text-primary ${
                  location.pathname.includes('/skincare')
                    ? 'font-bold text-primary underline underline-offset-8'
                    : 'text-muted-fg'
                }`}
              >
                Skincare
              </Link>
              <Link
                to="/category/sun-care"
                className={`transition-colors hover:text-primary ${
                  location.pathname.includes('/sun-care')
                    ? 'font-bold text-primary underline underline-offset-8'
                    : 'text-muted-fg'
                }`}
              >
                Sun Care
              </Link>
              <Link
                to="/category/hair-care"
                className={`transition-colors hover:text-primary ${
                  location.pathname.includes('/hair-care')
                    ? 'font-bold text-primary underline underline-offset-8'
                    : 'text-muted-fg'
                }`}
              >
                Hair Care
              </Link>
              <Link
                to="/category/fragrance"
                className={`transition-colors hover:text-primary ${
                  location.pathname.includes('/fragrance')
                    ? 'font-bold text-primary underline underline-offset-8'
                    : 'text-muted-fg'
                }`}
              >
                Fragrance
              </Link>
              <Link
                to="/category/beauty-tools"
                className={`transition-colors hover:text-primary ${
                  location.pathname.includes('/beauty-tools')
                    ? 'font-bold text-primary underline underline-offset-8'
                    : 'text-muted-fg'
                }`}
              >
                Tools &amp; Brushes
              </Link>
            </div>

            <div className="flex items-center gap-4 text-muted-fg">
              <a
                href="/#skin-routine-builder"
                className="inline-flex items-center gap-1 rounded-full bg-blush/60 px-2.5 py-1 text-[11px] font-semibold text-rose transition-colors hover:bg-blush"
              >
                <Sparkles className="h-3 w-3" />
                <span>Routine Quiz</span>
              </a>
              <Link to="/orders" className="hover:text-primary">
                Order Tracking
              </Link>
              <Link to="/support" className="hover:text-primary">
                Customer Care
              </Link>
            </div>
          </div>
        </nav>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="border-t border-border bg-card p-4 shadow-xl md:hidden">
            <form onSubmit={handleSearch} className="mb-4 flex gap-2">
              <input
                type="search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search cosmetics, brands..."
                className="flex-1 rounded-lg border border-border px-3 py-2 text-sm"
              />
              <button
                type="submit"
                className="touch-target rounded-lg bg-primary px-4 text-sm font-semibold text-primary-fg"
              >
                Go
              </button>
            </form>
            <div className="grid grid-cols-2 gap-2 text-sm font-medium">
              <Link to="/catalog" onClick={() => setMobileMenuOpen(false)} className="touch-target flex items-center rounded-lg p-2 hover:bg-muted">
                All Products
              </Link>
              <Link to="/category/skincare" onClick={() => setMobileMenuOpen(false)} className="touch-target flex items-center rounded-lg p-2 hover:bg-muted">
                Skincare
              </Link>
              <Link to="/category/makeup" onClick={() => setMobileMenuOpen(false)} className="touch-target flex items-center rounded-lg p-2 hover:bg-muted">
                Makeup
              </Link>
              <Link to="/category/sun-care" onClick={() => setMobileMenuOpen(false)} className="touch-target flex items-center rounded-lg p-2 hover:bg-muted">
                Sun Care
              </Link>
              <Link to="/category/hair-care" onClick={() => setMobileMenuOpen(false)} className="touch-target flex items-center rounded-lg p-2 hover:bg-muted">
                Hair Care
              </Link>
              <Link to="/category/fragrance" onClick={() => setMobileMenuOpen(false)} className="touch-target flex items-center rounded-lg p-2 hover:bg-muted">
                Fragrance
              </Link>
              <Link to="/category/beauty-tools" onClick={() => setMobileMenuOpen(false)} className="touch-target flex items-center rounded-lg p-2 hover:bg-muted">
                Tools &amp; Brushes
              </Link>
              <Link to="/orders" onClick={() => setMobileMenuOpen(false)} className="touch-target flex items-center rounded-lg p-2 hover:bg-muted">
                Order History
              </Link>
              <Link to="/support" onClick={() => setMobileMenuOpen(false)} className="touch-target flex items-center rounded-lg p-2 hover:bg-muted">
                Customer Service
              </Link>
              {user ? (
                <Link to="/profile" onClick={() => setMobileMenuOpen(false)} className="touch-target col-span-2 flex items-center rounded-lg bg-muted p-2 font-semibold">
                  Profile &amp; Addresses ({user.full_name})
                </Link>
              ) : (
                <Link to="/login" onClick={() => setMobileMenuOpen(false)} className="touch-target col-span-2 flex items-center justify-center rounded-lg bg-primary p-2.5 font-semibold text-primary-fg">
                  Sign In / Register
                </Link>
              )}
            </div>
          </div>
        )}
      </header>

      {/* Main Page Content */}
      <main id="main-content" className="mx-auto w-full max-w-7xl flex-1 px-4 py-8 sm:px-6">
        <Outlet />
      </main>

      {/* Modern Floating Back to Top Button */}
      <button
        type="button"
        onClick={scrollToTop}
        aria-label="Scroll back to top"
        className="touch-target fixed bottom-6 right-6 z-30 inline-flex items-center justify-center rounded-full border border-border bg-card/90 p-3 text-muted-fg shadow-lg backdrop-blur-md transition-all duration-200 hover:border-primary hover:text-primary hover:shadow-xl focus:outline-none"
      >
        <ArrowUp className="h-5 w-5" />
      </button>

      {/* Modern Luxury Editorial Footer */}
      <footer className="border-t border-border/80 bg-gradient-to-b from-beige/50 via-card to-beige/70 py-12">
        {/* Trust Badges Strip */}
        <div className="mx-auto mb-10 max-w-7xl border-b border-border/60 pb-8 px-4 sm:px-6">
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div className="flex items-center gap-3">
              <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blush/80 text-rose">
                <ShieldCheck className="h-5 w-5" />
              </span>
              <div>
                <p className="text-xs font-bold text-foreground">100% Authentic</p>
                <p className="text-[11px] text-muted-fg">Direct brand sourcing</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-beige text-accent">
                <Award className="h-5 w-5" />
              </span>
              <div>
                <p className="text-xs font-bold text-foreground">FEFO Freshness</p>
                <p className="text-[11px] text-muted-fg">Automated expiry protection</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blush/80 text-primary">
                <Truck className="h-5 w-5" />
              </span>
              <div>
                <p className="text-xs font-bold text-foreground">Fast Dispatch</p>
                <p className="text-[11px] text-muted-fg">Tracked demo shipments</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-beige text-rose">
                <RotateCcw className="h-5 w-5" />
              </span>
              <div>
                <p className="text-xs font-bold text-foreground">Seamless Returns</p>
                <p className="text-[11px] text-muted-fg">Customer-first guarantee</p>
              </div>
            </div>
          </div>
        </div>

        <div className="mx-auto grid max-w-7xl gap-8 px-4 sm:grid-cols-2 lg:grid-cols-4 sm:px-6">
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary text-primary-fg">
                <Sparkles className="h-4 w-4 text-amber-300" />
              </span>
              <h3 className="font-serif text-2xl font-bold text-primary">GlowCart</h3>
            </div>
            <p className="text-xs leading-relaxed text-muted-fg">
              A high-precision cosmetic atelier and batch-aware beauty platform. Curating iconic global
              brands alongside authentic Myanmar botanical heritage.
            </p>
            <div className="pt-2 text-[11px] font-mono text-muted-fg">
              Demo Storefront · Final Project Architecture
            </div>
          </div>

          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-rose">Curated Collections</h4>
            <ul className="mt-3 space-y-2 text-xs text-muted-fg">
              <li><Link to="/catalog" className="transition-colors hover:text-primary">All Cosmetics</Link></li>
              <li><Link to="/category/skincare" className="transition-colors hover:text-primary">Skincare &amp; Hydration</Link></li>
              <li><Link to="/category/makeup" className="transition-colors hover:text-primary">Foundations &amp; Lip Shades</Link></li>
              <li><Link to="/category/sun-care" className="transition-colors hover:text-primary">Sun Sticks &amp; UV Defense</Link></li>
              <li><Link to="/category/fragrance" className="transition-colors hover:text-primary">Luxury Eau de Parfum</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-rose">Customer Concierge</h4>
            <ul className="mt-3 space-y-2 text-xs text-muted-fg">
              <li><Link to="/orders" className="transition-colors hover:text-primary">Order Tracking</Link></li>
              <li><Link to="/support" className="transition-colors hover:text-primary">Customer Care &amp; Inquiries</Link></li>
              <li><Link to="/about" className="transition-colors hover:text-primary">About Our Atelier</Link></li>
              <li><Link to="/contact" className="transition-colors hover:text-primary">Contact &amp; Showroom</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-rose">Governance &amp; Portal</h4>
            <ul className="mt-3 space-y-2 text-xs text-muted-fg">
              <li><Link to="/privacy" className="transition-colors hover:text-primary">Privacy Policy</Link></li>
              <li><Link to="/terms" className="transition-colors hover:text-primary">Terms of Service</Link></li>
              <li><Link to="/admin/login" className="transition-colors hover:text-primary font-semibold text-foreground">Admin Portal Login</Link></li>
            </ul>
            <div className="mt-4 rounded-xl border border-border/80 bg-card/60 p-3 text-[11px] text-muted-fg">
              Protected by Argon2id password hashing, FEFO batch allocation, and JWT authorization.
            </div>
          </div>
        </div>

        <div className="mx-auto mt-10 max-w-7xl border-t border-border/60 pt-6 text-center text-xs text-muted-fg px-4 sm:px-6">
          © {new Date().getFullYear()} GlowCart Atelier. All rights reserved. Built with React, TypeScript, FastAPI &amp; PostgreSQL.
        </div>
      </footer>
      <AtelierBagToast />
    </div>
  );
};

