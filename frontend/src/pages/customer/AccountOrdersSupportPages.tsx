import React, { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { authApi, engagementApi, orderApi } from '@/services/api';
import { useAuthStore } from '@/store/authStore';
import { AlertBox, Badge, Button, Card } from '@/components/common/UI';

const TIMELINE_STEPS = ['PENDING', 'PAYMENT_PENDING', 'CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED'];

export const OrderHistoryPage: React.FC = () => {
  const { data: orders } = useQuery({
    queryKey: ['my-orders'],
    queryFn: orderApi.listOrders,
  });

  return (
    <div className="space-y-6">
      <h1 className="font-serif text-3xl font-bold">Order History</h1>
      {!orders || orders.length === 0 ? (
        <Card className="py-10 text-center text-sm text-muted-fg">No orders placed yet.</Card>
      ) : (
        <div className="space-y-4">
          {orders.map((o) => (
            <Card key={o.id} className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <Link to={`/orders/${o.id}`} className="font-mono text-base font-bold text-primary hover:underline">
                  {o.order_number}
                </Link>
                <div className="text-xs text-muted-fg">
                  {new Date(o.created_at).toLocaleDateString()} · {o.items.length} item(s)
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Badge tone="blush">{o.status}</Badge>
                <Badge tone={o.payment_status === 'PAID' ? 'success' : 'neutral'}>
                  {o.payment_status}
                </Badge>
                <span className="font-mono font-semibold">${Number(o.total_amount).toFixed(2)}</span>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export const OrderDetailsPage: React.FC = () => {
  const { orderId } = useParams<{ orderId: string }>();
  const queryClient = useQueryClient();
  const { data: order } = useQuery({
    queryKey: ['order', orderId],
    queryFn: () => orderApi.getOrder(orderId!),
    enabled: Boolean(orderId),
  });

  if (!order) return <div className="py-10 text-center">Loading order...</div>;

  const canCancel = ['PENDING', 'PAYMENT_PENDING', 'CONFIRMED'].includes(order.status);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="font-serif text-3xl font-bold">Order {order.order_number}</h1>
          <p className="text-sm text-muted-fg">
            Payment: {order.payment_method} ({order.payment_status})
          </p>
        </div>
        {canCancel && (
          <Button
            variant="danger"
            onClick={async () => {
              await orderApi.cancelOrder(order.id);
              queryClient.invalidateQueries({ queryKey: ['order', orderId] });
            }}
          >
            Cancel Order
          </Button>
        )}
      </div>

      <Card>
        <h2 className="mb-3 text-sm font-semibold">Tracking Progress</h2>
        <div className="flex flex-wrap gap-2">
          {TIMELINE_STEPS.map((step) => (
            <Badge key={step} tone={order.status === step ? 'blush' : 'neutral'}>
              {step}
            </Badge>
          ))}
          {['CANCELLED', 'REFUNDED', 'PAID'].includes(order.status) && (
            <Badge tone="warning">{order.status}</Badge>
          )}
        </div>
        {order.tracking_number && (
          <p className="mt-3 font-mono text-xs">Tracking #: {order.tracking_number}</p>
        )}
      </Card>

      <Card className="space-y-3">
        <h2 className="text-sm font-semibold">Order Item Snapshots</h2>
        {order.items.map((item) => (
          <div key={item.id} className="flex justify-between border-b border-border pb-2 text-sm">
            <div>
              <div className="font-medium">{item.product_name_snapshot}</div>
              <div className="text-xs text-muted-fg">
                {item.variant_label_snapshot} · SKU {item.variant_sku_snapshot} × {item.quantity}
              </div>
            </div>
            <span className="font-mono font-semibold">${Number(item.line_total).toFixed(2)}</span>
          </div>
        ))}
        <div className="flex justify-between pt-2 font-mono font-bold">
          <span>Total</span>
          <span>${Number(order.total_amount).toFixed(2)}</span>
        </div>
      </Card>
    </div>
  );
};

export const ProfileAddressesPage: React.FC = () => {
  const { user, hydrate } = useAuthStore();
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [phone, setPhone] = useState(user?.phone || '');
  const [savedMsg, setSavedMsg] = useState('');
  const { data: addresses, refetch } = useQuery({
    queryKey: ['addresses'],
    queryFn: authApi.listAddresses,
  });

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    await authApi.updateProfile({ full_name: fullName, phone });
    await hydrate();
    setSavedMsg('Profile updated.');
  };

  return (
    <div className="grid gap-8 md:grid-cols-2">
      <Card className="space-y-4">
        <h1 className="font-serif text-2xl font-bold">My Profile</h1>
        {savedMsg && <AlertBox message={savedMsg} tone="info" />}
        <form onSubmit={handleSave} className="space-y-3">
          <input
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Full name"
            className="w-full rounded-lg border border-border px-3 py-2 text-sm"
          />
          <input
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="Phone"
            className="w-full rounded-lg border border-border px-3 py-2 text-sm"
          />
          <Button type="submit">Update Profile</Button>
        </form>
      </Card>

      <Card className="space-y-4">
        <h2 className="font-serif text-2xl font-bold">Saved Addresses</h2>
        {addresses?.map((a) => (
          <div key={a.id} className="flex items-start justify-between border-b border-border pb-3 text-sm">
            <div>
              <strong>{a.label}</strong> — {a.recipient_name}
              <div className="text-xs text-muted-fg">
                {a.line1}, {a.city}, {a.postal_code}, {a.country}
              </div>
            </div>
            <Button
              variant="outline"
              onClick={async () => {
                await authApi.deleteAddress(a.id);
                refetch();
              }}
            >
              Delete
            </Button>
          </div>
        ))}
      </Card>
    </div>
  );
};

export const CustomerServicePage: React.FC = () => {
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const { data: messages, refetch } = useQuery({
    queryKey: ['messages'],
    queryFn: engagementApi.listMessages,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await engagementApi.createMessage({ subject, message });
    setSubject('');
    setMessage('');
    refetch();
  };

  return (
    <div className="grid gap-8 md:grid-cols-2">
      <Card className="space-y-4">
        <h1 className="font-serif text-2xl font-bold">Customer Service</h1>
        <form onSubmit={handleSubmit} className="space-y-3">
          <input
            required
            placeholder="Subject"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            className="w-full rounded-lg border border-border px-3 py-2 text-sm"
          />
          <textarea
            required
            rows={4}
            placeholder="How can our beauty & order support team help?"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="w-full rounded-lg border border-border px-3 py-2 text-sm"
          />
          <Button type="submit">Send Message</Button>
        </form>
      </Card>

      <div className="space-y-4">
        <h2 className="font-serif text-2xl font-bold">Message History</h2>
        {messages?.map((m) => (
          <Card key={m.id} className="space-y-2">
            <div className="flex justify-between">
              <strong>{m.subject}</strong>
              <Badge tone="blush">{m.status}</Badge>
            </div>
            <p className="text-sm text-muted-fg">{m.message}</p>
            {m.replies.map((r) => (
              <div key={r.id} className="rounded-lg bg-beige p-2 text-xs">
                <strong>Admin Reply:</strong> {r.body}
              </div>
            ))}
          </Card>
        ))}
      </div>
    </div>
  );
};

export const NotificationsPage: React.FC = () => {
  const { data: items, refetch } = useQuery({
    queryKey: ['notifications'],
    queryFn: engagementApi.listNotifications,
  });

  return (
    <div className="space-y-4">
      <h1 className="font-serif text-3xl font-bold">Notifications</h1>
      {items?.map((n) => (
        <Card key={n.id} className="flex items-center justify-between gap-4">
          <div>
            <div className="font-semibold">{n.title}</div>
            <p className="text-sm text-muted-fg">{n.body}</p>
          </div>
          {!n.is_read && (
            <Button
              variant="outline"
              onClick={async () => {
                await engagementApi.markRead(n.id);
                refetch();
              }}
            >
              Mark Read
            </Button>
          )}
        </Card>
      ))}
    </div>
  );
};

