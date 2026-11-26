import React, { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Trash2 } from 'lucide-react';
import { authApi, cartApi, orderApi } from '@/services/api';
import { useCartStore } from '@/store/cartStore';
import { AlertBox, Badge, Button, Card } from '@/components/common/UI';

export const CartPage: React.FC = () => {
  const { cart, fetchCart, setCart } = useCartStore();
  const [couponInput, setCouponInput] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  if (!cart || cart.items.length === 0) {
    return (
      <Card className="py-12 text-center space-y-4">
        <h1 className="font-serif text-3xl font-bold">Your Shopping Cart is Empty</h1>
        <p className="text-sm text-muted-fg">Discover curated beauty essentials in our catalog.</p>
        <Link
          to="/catalog"
          className="touch-target inline-flex items-center rounded-lg bg-primary px-5 py-2.5 text-sm font-medium text-primary-fg"
        >
          Browse Catalog
        </Link>
      </Card>
    );
  }

  return (
    <div className="grid gap-8 lg:grid-cols-[1fr_360px]">
      <div className="space-y-4">
        <h1 className="font-serif text-3xl font-bold">Shopping Cart</h1>
        {cart.items.map((item) => (
          <Card key={item.id} className="flex flex-wrap items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="text-xs uppercase text-muted-fg">{item.brand_name}</div>
              <Link to={`/products/${item.product_id}`} className="font-semibold hover:text-primary">
                {item.product_name}
              </Link>
              <div className="text-xs text-muted-fg">
                {item.shade_name || (item.volume_ml ? `${item.volume_ml} ml` : item.size)} · SKU:{' '}
                <span className="font-mono">{item.sku}</span>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <input
                type="number"
                min={1}
                max={item.available_quantity}
                aria-label={`Quantity for ${item.product_name}`}
                value={item.quantity}
                onChange={async (e) => {
                  const qty = Math.max(1, Number(e.target.value));
                  const updated = await cartApi.updateItem(item.id, qty);
                  setCart(updated);
                }}
                className="touch-target w-20 rounded-lg border border-border px-2 py-1.5 text-center font-mono text-sm"
              />
              <span className="w-20 text-right font-mono font-semibold">
                ${Number(item.line_total).toFixed(2)}
              </span>
              <button
                type="button"
                aria-label={`Remove ${item.product_name}`}
                onClick={async () => {
                  const updated = await cartApi.removeItem(item.id);
                  setCart(updated);
                }}
                className="touch-target rounded-lg p-2 text-muted-fg hover:text-destructive"
              >
                <Trash2 className="h-4 w-4" aria-hidden="true" />
              </button>
            </div>
          </Card>
        ))}
      </div>

      <Card className="h-fit space-y-4">
        <h2 className="font-serif text-xl font-bold">Order Summary</h2>
        <div className="flex gap-2">
          <input
            type="text"
            value={couponInput}
            onChange={(e) => setCouponInput(e.target.value)}
            placeholder="Coupon code (e.g. GLOW15)"
            className="flex-1 rounded-lg border border-border px-3 py-2 text-sm font-mono uppercase"
          />
          <Button type="button" variant="outline" onClick={() => fetchCart(couponInput)}>
            Apply
          </Button>
        </div>
        {cart.coupon_message && <AlertBox message={cart.coupon_message} tone="info" />}
        <dl className="space-y-2 border-t border-border pt-3 text-sm">
          <div className="flex justify-between">
            <dt className="text-muted-fg">Subtotal</dt>
            <dd className="font-mono">${Number(cart.subtotal).toFixed(2)}</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-muted-fg">Discount</dt>
            <dd className="font-mono text-accent">-${Number(cart.discount_amount).toFixed(2)}</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-muted-fg">Shipping</dt>
            <dd className="font-mono">${Number(cart.shipping_fee).toFixed(2)}</dd>
          </div>
          <div className="flex justify-between border-t border-border pt-2 text-base font-bold">
            <dt>Total (USD)</dt>
            <dd className="font-mono">${Number(cart.total_amount).toFixed(2)}</dd>
          </div>
        </dl>
        <Button type="button" className="w-full bg-mauve-deep text-white hover:bg-plum" onClick={() => navigate('/checkout')}>
          Proceed to Checkout
        </Button>
      </Card>
    </div>
  );
};

export const WishlistPage: React.FC = () => {
  const { data, refetch } = useQuery({
    queryKey: ['wishlist'],
    queryFn: cartApi.getWishlist,
  });

  return (
    <div className="space-y-6">
      <h1 className="font-serif text-3xl font-bold">Saved Wishlist</h1>
      {!data || data.items.length === 0 ? (
        <Card className="py-10 text-center text-sm text-muted-fg">
          No saved cosmetics yet.
        </Card>
      ) : (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {data.items.map((item) => (
            <Card key={item.id} className="space-y-3">
              <Link to={`/products/${item.product_id}`} className="font-semibold hover:text-primary">
                {item.product_name}
              </Link>
              <div className="text-xs text-muted-fg">{item.brand_name}</div>
              <div className="flex items-center justify-between">
                <span className="font-mono font-semibold">
                  {item.min_price ? `$${Number(item.min_price).toFixed(2)}` : ''}
                </span>
                <Button
                  variant="outline"
                  onClick={async () => {
                    await cartApi.removeWishlist(item.id);
                    refetch();
                  }}
                >
                  Remove
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export const CheckoutPage: React.FC = () => {
  const { cart, fetchCart, resetCart } = useCartStore();
  const navigate = useNavigate();
  const { data: addresses, refetch: refetchAddresses } = useQuery({
    queryKey: ['addresses'],
    queryFn: authApi.listAddresses,
  });

  const [selectedAddress, setSelectedAddress] = useState('');
  const [paymentMethod, setPaymentMethod] = useState<'COD' | 'SANDBOX'>('COD');
  const [couponCode, setCouponCode] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const [newLine1, setNewLine1] = useState('');
  const [newCity, setNewCity] = useState('');
  const [newCountry, setNewCountry] = useState('United States');
  const [newRecipient, setNewRecipient] = useState('');
  const [newPhone, setNewPhone] = useState('');
  const [newPostal, setNewPostal] = useState('');

  useEffect(() => {
    fetchCart(couponCode || undefined);
  }, [fetchCart, couponCode]);

  useEffect(() => {
    if (addresses && addresses.length > 0 && !selectedAddress) {
      const def = addresses.find((a) => a.is_default) || addresses[0];
      setSelectedAddress(def.id);
    }
  }, [addresses, selectedAddress]);

  const handleAddAddress = async (e: React.FormEvent) => {
    e.preventDefault();
    const created = await authApi.createAddress({
      label: 'Delivery',
      recipient_name: newRecipient,
      phone: newPhone,
      line1: newLine1,
      city: newCity,
      postal_code: newPostal,
      country: newCountry,
      is_default: true,
    });
    await refetchAddresses();
    setSelectedAddress(created.id);
    setNewLine1('');
  };

  const handlePlaceOrder = async () => {
    setError('');
    if (!selectedAddress) {
      setError('Please select or create a delivery address.');
      return;
    }
    setSubmitting(true);
    try {
      const idempotencyKey = `web-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
      const order = await orderApi.createOrder({
        address_id: selectedAddress,
        payment_method: paymentMethod,
        coupon_code: couponCode || undefined,
        idempotency_key: idempotencyKey,
      });
      if (paymentMethod === 'SANDBOX') {
        await orderApi.initiatePayment(order.id);
      }
      resetCart();
      navigate(`/order-confirmation/${order.id}`);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg || 'Order could not be completed.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="grid gap-8 lg:grid-cols-[1fr_360px]">
      <div className="space-y-6">
        <h1 className="font-serif text-3xl font-bold">Checkout</h1>
        {error && <AlertBox message={error} />}

        <Card className="space-y-4">
          <h2 className="text-lg font-semibold">1. Delivery Address</h2>
          <div className="grid gap-3 sm:grid-cols-2">
            {addresses?.map((addr) => (
              <label
                key={addr.id}
                className={`cursor-pointer rounded-xl border p-3 text-sm ${
                  selectedAddress === addr.id ? 'border-primary bg-blush/20' : 'border-border'
                }`}
              >
                <input
                  type="radio"
                  name="address"
                  checked={selectedAddress === addr.id}
                  onChange={() => setSelectedAddress(addr.id)}
                  className="mr-2"
                />
                <strong>{addr.recipient_name}</strong>
                <div className="text-xs text-muted-fg">
                  {addr.line1}, {addr.city}, {addr.postal_code}, {addr.country}
                </div>
              </label>
            ))}
          </div>
          <form onSubmit={handleAddAddress} className="grid gap-2 border-t border-border pt-4 sm:grid-cols-2">
            <input
              placeholder="Recipient Name"
              required
              value={newRecipient}
              onChange={(e) => setNewRecipient(e.target.value)}
              className="rounded-lg border border-border px-3 py-2 text-sm"
            />
            <input
              placeholder="Phone"
              required
              value={newPhone}
              onChange={(e) => setNewPhone(e.target.value)}
              className="rounded-lg border border-border px-3 py-2 text-sm"
            />
            <input
              placeholder="Address Line 1"
              required
              value={newLine1}
              onChange={(e) => setNewLine1(e.target.value)}
              className="sm:col-span-2 rounded-lg border border-border px-3 py-2 text-sm"
            />
            <input
              placeholder="City"
              required
              value={newCity}
              onChange={(e) => setNewCity(e.target.value)}
              className="rounded-lg border border-border px-3 py-2 text-sm"
            />
            <input
              placeholder="Postal Code"
              required
              value={newPostal}
              onChange={(e) => setNewPostal(e.target.value)}
              className="rounded-lg border border-border px-3 py-2 text-sm"
            />
            <input
              placeholder="Country"
              required
              value={newCountry}
              onChange={(e) => setNewCountry(e.target.value)}
              className="sm:col-span-2 rounded-lg border border-border px-3 py-2 text-sm"
            />
            <Button type="submit" variant="outline" className="sm:col-span-2">
              Save New Address
            </Button>
          </form>
        </Card>

        <Card className="space-y-3">
          <h2 className="text-lg font-semibold">2. Payment Method</h2>
          <label className="flex items-center gap-3 rounded-lg border border-border p-3 text-sm">
            <input
              type="radio"
              name="payment"
              checked={paymentMethod === 'COD'}
              onChange={() => setPaymentMethod('COD')}
            />
            <div>
              <strong>Cash on Delivery (COD)</strong>
              <p className="text-xs text-muted-fg">Pay in cash when your parcel arrives.</p>
            </div>
          </label>
          <label className="flex items-center gap-3 rounded-lg border border-border p-3 text-sm">
            <input
              type="radio"
              name="payment"
              checked={paymentMethod === 'SANDBOX'}
              onChange={() => setPaymentMethod('SANDBOX')}
            />
            <div>
              <strong>Online Payment Sandbox</strong>
              <p className="text-xs text-muted-fg">
                Development sandbox gateway verified via server-side webhook.
              </p>
            </div>
          </label>
        </Card>
      </div>

      <Card className="h-fit space-y-4">
        <h2 className="font-serif text-xl font-bold">Review Order</h2>
        <input
          type="text"
          value={couponCode}
          onChange={(e) => setCouponCode(e.target.value)}
          placeholder="Optional coupon code"
          className="w-full rounded-lg border border-border px-3 py-2 font-mono text-sm uppercase"
        />
        {cart && (
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between">
              <dt className="text-muted-fg">Items ({cart.items.length})</dt>
              <dd className="font-mono">${Number(cart.subtotal).toFixed(2)}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-muted-fg">Discount</dt>
              <dd className="font-mono text-accent">-${Number(cart.discount_amount).toFixed(2)}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-muted-fg">Shipping</dt>
              <dd className="font-mono">${Number(cart.shipping_fee).toFixed(2)}</dd>
            </div>
            <div className="flex justify-between border-t border-border pt-2 text-base font-bold">
              <dt>Total</dt>
              <dd className="font-mono">${Number(cart.total_amount).toFixed(2)}</dd>
            </div>
          </dl>
        )}
        <Button type="button" onClick={handlePlaceOrder} disabled={submitting} className="w-full">
          {submitting ? 'Confirming...' : 'Confirm Purchase'}
        </Button>
      </Card>
    </div>
  );
};

export const OrderConfirmationPage: React.FC = () => {
  const { orderId } = useParams<{ orderId: string }>();
  const { data: order } = useQuery({
    queryKey: ['order', orderId],
    queryFn: () => orderApi.getOrder(orderId!),
    enabled: Boolean(orderId),
  });

  if (!order) return <div className="py-10 text-center">Loading order confirmation...</div>;

  return (
    <Card className="mx-auto max-w-2xl space-y-4">
      <Badge tone="success">Order Recorded</Badge>
      <h1 className="font-serif text-3xl font-bold">Order {order.order_number}</h1>
      <p className="text-sm text-muted-fg">
        Status: <strong>{order.status}</strong> · Payment: <strong>{order.payment_status}</strong>
      </p>
      <div className="border-t border-border pt-3 text-sm">
        Total Paid / Due: <strong className="font-mono">${Number(order.total_amount).toFixed(2)}</strong>
      </div>
      <Link
        to={`/orders/${order.id}`}
        className="touch-target inline-flex items-center rounded-lg bg-primary px-5 py-2.5 text-sm font-medium text-primary-fg"
      >
        Track Order Details
      </Link>
    </Card>
  );
};

export const PaymentResultPage: React.FC = () => (
  <Card className="mx-auto max-w-lg space-y-4 text-center">
    <h1 className="font-serif text-3xl font-bold">Payment Verification Status</h1>
    <p className="text-sm text-muted-fg">
      Online payments are confirmed strictly via server-side provider webhook verification. Check
      your order history for live payment status.
    </p>
    <Link
      to="/orders"
      className="touch-target inline-flex items-center rounded-lg bg-primary px-5 py-2.5 text-sm font-medium text-primary-fg"
    >
      View My Orders
    </Link>
  </Card>
);

