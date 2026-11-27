import React, { useState } from 'react';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import {
  ArrowUp,
  Check,
  Copy,
  Headphones,
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
import { useQuickViewStore } from '@/store/quickViewStore';
import { AtelierBagToast } from '@/components/customer/AtelierBagToast';
import { QuickViewModal } from '@/components/customer/QuickViewModal';

const NAV_LINKS = [
  { to: '/', label: 'Home', exact: true },
  { to: '/catalog', label: 'Shop' },
  { to: '/category/makeup', label: 'Makeup' },
  { to: '/category/skincare', label: 'Skincare' },
  { to: '/category/sun-care', label: 'Sun Care' },
  { to: '/category/hair-care', label: 'Hair Care' },
  { to: '/category/fragrance', label: 'Fragrance' },
  { to: '/category/beauty-tools', label: 'Tools & Brushes' },
];

export const CustomerLayout: React.FC = () => {
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [copiedCode, setCopiedCode] = useState(false);
  const [newsletterEmail, setNewsletterEmail] = useState('');
  const [newsletterSubscribed, setNewsletterSubscribed] = useState(false);

  const navigate = useNavigate();
  const location = useLocation();
  const { user, clearSession } = useAuthStore();
  const { itemCount, resetCart } = useCartStore();
  const quickViewProduct = useQuickViewStore((s) => s.product);
  const closeQuickView = useQuickViewStore((s) => s.closeQuickView);

  React.useEffect(() => {
    closeQuickView();
  }, [location.pathname, closeQuickView]);

  const isHome = location.pathname === '/';

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
      setSearchOpen(false);
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

  const handleSubscribe = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newsletterEmail.trim()) return;
    setNewsletterSubscribed(true);
    setNewsletterEmail('');
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const isLinkActive = (to: string, exact?: boolean) => {
    if (exact) return location.pathname === to;
    if (to === '/catalog') return location.pathname === '/catalog' || location.pathname === '/products';
    return location.pathname.startsWith(to);
  };

  return (
    <div className="flex min-h-screen flex-col bg-cream-warm text-foreground selection:bg-blush selection:text-plum">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-plum focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-white shadow-lg"
      >
        Skip to main content
      </a>

      {/* 1A. Top Full-Width Dusty-Mauve Announcement Bar */}
      <div className="relative z-40 bg-mauve-deep px-4 py-2 text-center text-xs font-medium text-white">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-center gap-2">
          <span>Free International Delivery on Orders Over $75</span>
          <span className="opacity-60" aria-hidden="true">|</span>
          <span className="inline-flex items-center gap-1.5">
            <span>Use Code:</span>
            <button
              type="button"
              onClick={handleCopyCode}
              title="Click to copy 15% discount code"
              className="inline-flex cursor-pointer items-center gap-1 rounded-full bg-white/15 px-2.5 py-0.5 font-mono text-[11px] font-bold tracking-wider text-white transition-colors hover:bg-white/25 focus-visible:ring-2 focus-visible:ring-white"
            >
              <span>GLOW15</span>
              {copiedCode ? (
                <Check className="h-3 w-3 text-emerald-200" aria-hidden="true" />
              ) : (
                <Copy className="h-3 w-3 opacity-80" aria-hidden="true" />
              )}
            </button>
            <span>for 15% OFF</span>
          </span>
        </div>
      </div>

      {/* 1B. Sticky 3-Part Clean White Header */}
      <header className="sticky top-0 z-30 border-b border-border/70 bg-card/95 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3.5 sm:px-6">
          {/* Left: Mobile Menu Trigger + GlowCart Serif Logo */}
          <div className="flex items-center gap-3 shrink-0">
            <button
              type="button"
              onClick={() => setMobileMenuOpen((v) => !v)}
              aria-label="Toggle navigation menu"
              aria-expanded={mobileMenuOpen}
              className="touch-target inline-flex items-center justify-center rounded-xl border border-border/80 bg-card p-2 text-foreground transition-colors hover:bg-muted lg:hidden"
            >
              {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>

            <Link to="/" className="group flex flex-col">
              <span className="font-serif text-2xl font-bold leading-none tracking-tight text-plum transition-colors group-hover:text-mauve-deep sm:text-3xl">
                GlowCart
              </span>
              <span className="mt-0.5 text-[9px] font-semibold uppercase tracking-[0.26em] text-muted-fg">
                ATELIER DE BEAUTÉ
              </span>
            </Link>
          </div>

          {/* Center: Horizontal Navigation Links */}
          <nav aria-label="Main navigation" className="hidden items-center justify-center gap-5 xl:gap-7 lg:flex">
            {NAV_LINKS.map((item) => {
              const active = isLinkActive(item.to, item.exact);
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className={`whitespace-nowrap text-[13px] font-medium tracking-wide transition-colors hover:text-mauve-deep ${
                    active
                      ? 'font-semibold text-plum underline decoration-mauve-deep decoration-2 underline-offset-8'
                      : 'text-foreground/80'
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>

          {/* Right: Search, Wishlist, Account, Shopping Bag */}
          <div className="flex items-center gap-1 sm:gap-1.5 shrink-0">
            <button
              type="button"
              onClick={() => setSearchOpen((v) => !v)}
              aria-label="Toggle product search"
              aria-expanded={searchOpen}
              className="touch-target inline-flex items-center justify-center rounded-full p-2 text-foreground transition-colors hover:bg-blush-soft hover:text-plum"
            >
              <Search className="h-5 w-5" aria-hidden="true" />
            </button>

            <Link
              to="/wishlist"
              aria-label="Wishlist"
              className="touch-target inline-flex items-center justify-center rounded-full p-2 text-foreground transition-colors hover:bg-blush-soft hover:text-plum"
            >
              <Heart className="h-5 w-5" aria-hidden="true" />
            </Link>

            {user ? (
              <div className="hidden items-center gap-1 sm:flex">
                <Link
                  to="/profile"
                  aria-label="Account profile"
                  className="touch-target inline-flex items-center gap-1.5 rounded-full px-3 py-2 text-xs font-semibold text-foreground transition-colors hover:bg-blush-soft hover:text-plum"
                >
                  <UserIcon className="h-4 w-4 text-mauve-deep" aria-hidden="true" />
                  <span>{user.full_name?.split(' ')[0] || 'Account'}</span>
                </Link>
                {(user.role === 'admin' || user.role === 'super_admin') && (
                  <Link
                    to="/admin"
                    className="touch-target inline-flex items-center rounded-full bg-plum px-3 py-1.5 text-xs font-semibold text-white transition-opacity hover:opacity-90"
                  >
                    Admin
                  </Link>
                )}
                <button
                  type="button"
                  onClick={handleLogout}
                  className="touch-target rounded-full px-2.5 py-2 text-xs font-medium text-muted-fg transition-colors hover:text-foreground"
                >
                  Logout
                </button>
              </div>
            ) : (
              <Link
                to="/login"
                aria-label="Account sign in"
                className="touch-target inline-flex items-center justify-center rounded-full p-2 text-foreground transition-colors hover:bg-blush-soft hover:text-plum"
              >
                <UserIcon className="h-5 w-5" aria-hidden="true" />
              </Link>
            )}

            <Link
              to="/cart"
              aria-label="Shopping cart"
              className="touch-target relative inline-flex items-center justify-center rounded-full p-2 text-foreground transition-colors hover:bg-blush-soft hover:text-plum"
            >
              <ShoppingBag className="h-5 w-5" aria-hidden="true" />
              {itemCount > 0 && (
                <span className="absolute right-0.5 top-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-mauve-deep font-mono text-[11px] font-bold text-white shadow-sm">
                  {itemCount}
                </span>
              )}
            </Link>
          </div>
        </div>

        {/* Expandable Search Bar */}
        {searchOpen && (
          <div className="border-t border-border/60 bg-card px-4 py-3 sm:px-6">
            <form onSubmit={handleSearch} className="mx-auto flex max-w-2xl items-center gap-2">
              <label htmlFor="header-search" className="sr-only">
                Search beauty products
              </label>
              <div className="relative flex-1">
                <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-fg" aria-hidden="true" />
                <input
                  id="header-search"
                  type="search"
                  autoFocus
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search serums, lipsticks, SPF, fragrances, brushes..."
                  className="w-full rounded-full border border-border bg-cream-warm py-2.5 pl-10 pr-4 text-sm text-foreground focus:border-mauve-deep focus:bg-card focus:outline-none focus:ring-2 focus:ring-mauve/25"
                />
              </div>
              <button
                type="submit"
                className="touch-target rounded-full bg-mauve-deep px-5 py-2 text-xs font-semibold uppercase tracking-wider text-white transition-colors hover:bg-plum"
              >
                Search
              </button>
            </form>
          </div>
        )}

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="border-t border-border bg-card p-4 shadow-xl lg:hidden">
            <form onSubmit={handleSearch} className="mb-4 flex gap-2">
              <input
                type="search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search cosmetics, brands..."
                className="flex-1 rounded-full border border-border bg-cream-warm px-4 py-2 text-sm"
              />
              <button
                type="submit"
                className="touch-target rounded-full bg-mauve-deep px-4 text-xs font-semibold uppercase tracking-wider text-white"
              >
                Go
              </button>
            </form>
            <div className="grid grid-cols-2 gap-2 text-sm font-medium">
              {NAV_LINKS.map((item) => (
                <Link
                  key={item.to}
                  to={item.to}
                  onClick={() => setMobileMenuOpen(false)}
                  className="touch-target flex items-center rounded-lg px-3 py-2 hover:bg-blush-soft hover:text-plum"
                >
                  {item.label}
                </Link>
              ))}
              <Link
                to="/orders"
                onClick={() => setMobileMenuOpen(false)}
                className="touch-target flex items-center rounded-lg px-3 py-2 hover:bg-blush-soft"
              >
                Order History
              </Link>
              <Link
                to="/support"
                onClick={() => setMobileMenuOpen(false)}
                className="touch-target flex items-center rounded-lg px-3 py-2 hover:bg-blush-soft"
              >
                Customer Care
              </Link>
              {user ? (
                <Link
                  to="/profile"
                  onClick={() => setMobileMenuOpen(false)}
                  className="touch-target col-span-2 flex items-center rounded-lg bg-blush-soft px-3 py-2 font-semibold text-plum"
                >
                  Profile &amp; Addresses ({user.full_name})
                </Link>
              ) : (
                <Link
                  to="/login"
                  onClick={() => setMobileMenuOpen(false)}
                  className="touch-target col-span-2 flex items-center justify-center rounded-full bg-mauve-deep p-2.5 font-semibold text-white"
                >
                  Sign In / Register
                </Link>
              )}
            </div>
          </div>
        )}
      </header>

      {/* Main Page Content */}
      <main
        id="main-content"
        className={isHome ? 'w-full flex-1' : 'mx-auto w-full max-w-7xl flex-1 px-4 py-8 sm:px-6'}
      >
        <Outlet />
      </main>

      {/* Floating Back to Top Button */}
      <button
        type="button"
        onClick={scrollToTop}
        aria-label="Scroll back to top"
        className="touch-target fixed bottom-6 right-6 z-30 inline-flex items-center justify-center rounded-full border border-border bg-card/95 p-3 text-plum shadow-lg backdrop-blur-md transition-all duration-200 hover:border-mauve-deep hover:bg-blush-soft focus-visible:ring-2 focus-visible:ring-ring"
      >
        <ArrowUp className="h-5 w-5" aria-hidden="true" />
      </button>

      {/* 7. Service Guarantees Strip (Light Blush directly above Footer) */}
      <section aria-label="Service guarantees" className="border-t border-border/60 bg-blush-soft py-8">
        <div className="mx-auto grid max-w-7xl grid-cols-2 gap-6 px-4 sm:px-6 lg:grid-cols-4">
          <div className="flex items-center gap-3.5">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-card text-mauve-deep shadow-sm">
              <Truck className="h-5 w-5" aria-hidden="true" />
            </span>
            <div>
              <p className="text-sm font-semibold text-plum">Free Shipping</p>
              <p className="text-xs text-muted-fg">On orders over $75</p>
            </div>
          </div>
          <div className="flex items-center gap-3.5">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-card text-mauve-deep shadow-sm">
              <RotateCcw className="h-5 w-5" aria-hidden="true" />
            </span>
            <div>
              <p className="text-sm font-semibold text-plum">Easy Returns</p>
              <p className="text-xs text-muted-fg">15 days return policy</p>
            </div>
          </div>
          <div className="flex items-center gap-3.5">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-card text-mauve-deep shadow-sm">
              <ShieldCheck className="h-5 w-5" aria-hidden="true" />
            </span>
            <div>
              <p className="text-sm font-semibold text-plum">Secure Payment</p>
              <p className="text-xs text-muted-fg">100% secure checkout</p>
            </div>
          </div>
          <div className="flex items-center gap-3.5">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-card text-mauve-deep shadow-sm">
              <Headphones className="h-5 w-5" aria-hidden="true" />
            </span>
            <div>
              <p className="text-sm font-semibold text-plum">24/7 Support</p>
              <p className="text-xs text-muted-fg">We&apos;re here to help</p>
            </div>
          </div>
        </div>
      </section>

      {/* 8. 4-Column Deep Plum/Burgundy Luxury Footer */}
      <footer className="bg-plum text-white">
        <div className="mx-auto grid max-w-7xl gap-10 px-4 py-14 sm:grid-cols-2 lg:grid-cols-4 sm:px-6">
          {/* Col 1: Brand Logo & Social Links */}
          <div className="space-y-4">
            <div>
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-blush" aria-hidden="true" />
                <span className="font-serif text-3xl font-bold tracking-tight text-white">GlowCart</span>
              </div>
              <p className="mt-0.5 text-[10px] font-semibold uppercase tracking-[0.24em] text-blush/80">
                ATELIER DE BEAUTÉ
              </p>
            </div>
            <p className="text-xs leading-relaxed text-white/80">
              Clean, clinically proven beauty and batch-verified luxury essentials curated to nourish and elevate your daily ritual.
            </p>
            <div className="flex items-center gap-3 pt-1">
              <a
                href="https://instagram.com"
                target="_blank"
                rel="noreferrer"
                aria-label="GlowCart on Instagram"
                className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-white/20 text-xs font-semibold text-white/90 transition-colors hover:bg-white/15"
              >
                IG
              </a>
              <a
                href="https://tiktok.com"
                target="_blank"
                rel="noreferrer"
                aria-label="GlowCart on TikTok"
                className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-white/20 text-xs font-semibold text-white/90 transition-colors hover:bg-white/15"
              >
                TT
              </a>
              <a
                href="https://youtube.com"
                target="_blank"
                rel="noreferrer"
                aria-label="GlowCart on YouTube"
                className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-white/20 text-xs font-semibold text-white/90 transition-colors hover:bg-white/15"
              >
                YT
              </a>
            </div>
          </div>

          {/* Col 2: Quick Links */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-blush">Quick Links</h3>
            <ul className="mt-4 space-y-2.5 text-xs text-white/80">
              <li><Link to="/catalog" className="transition-colors hover:text-white">Shop All Products</Link></li>
              <li><Link to="/category/skincare" className="transition-colors hover:text-white">Skincare</Link></li>
              <li><Link to="/category/makeup" className="transition-colors hover:text-white">Makeup</Link></li>
              <li><Link to="/category/sun-care" className="transition-colors hover:text-white">Sun Care</Link></li>
              <li><Link to="/category/hair-care" className="transition-colors hover:text-white">Hair Care</Link></li>
              <li><Link to="/category/fragrance" className="transition-colors hover:text-white">Fragrance</Link></li>
              <li><Link to="/category/beauty-tools" className="transition-colors hover:text-white">Tools &amp; Brushes</Link></li>
            </ul>
          </div>

          {/* Col 3: Customer Care */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-blush">Customer Care</h3>
            <ul className="mt-4 space-y-2.5 text-xs text-white/80">
              <li><Link to="/orders" className="transition-colors hover:text-white">Order Tracking</Link></li>
              <li><Link to="/support" className="transition-colors hover:text-white">Customer Support</Link></li>
              <li><Link to="/about" className="transition-colors hover:text-white">About GlowCart</Link></li>
              <li><Link to="/contact" className="transition-colors hover:text-white">Contact Us</Link></li>
              <li><Link to="/privacy" className="transition-colors hover:text-white">Privacy Policy</Link></li>
              <li><Link to="/terms" className="transition-colors hover:text-white">Terms of Service</Link></li>
              <li><Link to="/admin/login" className="font-semibold text-blush transition-colors hover:text-white">Admin Portal</Link></li>
            </ul>
          </div>

          {/* Col 4: Newsletter */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-blush">Newsletter</h3>
            <p className="mt-4 text-xs leading-relaxed text-white/80">
              Join our atelier list for early access to limited drops, shade launches, and 15% off your first ritual.
            </p>
            <form onSubmit={handleSubscribe} className="mt-4 flex flex-col gap-2.5">
              <label htmlFor="footer-newsletter" className="sr-only">
                Email address for newsletter
              </label>
              <input
                id="footer-newsletter"
                type="email"
                required
                value={newsletterEmail}
                onChange={(e) => {
                  setNewsletterEmail(e.target.value);
                  if (newsletterSubscribed) setNewsletterSubscribed(false);
                }}
                placeholder="Enter your email address"
                className="min-h-[44px] w-full rounded-lg border border-white/25 bg-plum-dark/80 px-3.5 py-2.5 text-xs text-white placeholder:text-white/50 focus:border-blush focus:outline-none focus:ring-2 focus:ring-blush/30"
              />
              <button
                type="submit"
                className="touch-target w-full rounded-lg bg-mauve-deep px-4 py-2.5 text-xs font-bold uppercase tracking-[0.18em] text-white transition-colors hover:bg-mauve focus-visible:ring-2 focus-visible:ring-white"
              >
                SUBSCRIBE
              </button>
              {newsletterSubscribed && (
                <p className="text-[11px] font-medium text-emerald-200">
                  Thank you for subscribing to GlowCart Atelier.
                </p>
              )}
            </form>
          </div>
        </div>

        {/* Bottom Copyright & Payment Badges */}
        <div className="border-t border-white/15 bg-plum-dark/60">
          <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-4 py-5 text-xs text-white/75 sm:flex-row sm:px-6">
            <p>© {new Date().getFullYear()} GlowCart Atelier de Beauté. All rights reserved.</p>
            <div className="flex flex-wrap items-center gap-2" aria-label="Accepted payment methods">
              {['VISA', 'MASTERCARD', 'AMEX', 'APPLE PAY', 'STRIPE'].map((badge) => (
                <span
                  key={badge}
                  className="rounded border border-white/20 bg-white/10 px-2.5 py-1 font-mono text-[10px] font-semibold tracking-wider text-white/90"
                >
                  {badge}
                </span>
              ))}
            </div>
          </div>
        </div>
      </footer>

      <AtelierBagToast />
      {quickViewProduct && (
        <QuickViewModal
          product={quickViewProduct}
          isOpen={Boolean(quickViewProduct)}
          onClose={closeQuickView}
        />
      )}
    </div>
  );
};
