import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { adminApi, engagementApi } from '@/services/api';
import { Badge, Button, Card } from '@/components/common/UI';
import { useAuthStore } from '@/store/authStore';
import { API_BASE_URL } from '@/utils/apiConfig';

export const AdminOrdersPage: React.FC = () => {
  const { data: orders, refetch } = useQuery({ queryKey: ['admin-orders'], queryFn: adminApi.getOrders });

  return (
    <div className="space-y-6">
      <h1 className="font-serif text-3xl font-bold">Order Management</h1>
      <Card className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-border text-xs text-muted-fg">
              <th className="py-2">Order #</th><th>Status</th><th>Payment</th><th>Total</th><th>Update</th>
            </tr>
          </thead>
          <tbody>
            {orders?.map((o) => (
              <tr key={o.id} className="border-b border-border/60">
                <td className="py-2 font-mono">{o.order_number}</td>
                <td><Badge tone="blush">{o.status}</Badge></td>
                <td>{o.payment_method} ({o.payment_status})</td>
                <td className="font-mono">${Number(o.total_amount).toFixed(2)}</td>
                <td>
                  <select
                    aria-label={`Status for ${o.order_number}`}
                    value={o.status}
                    onChange={async (e) => {
                      await adminApi.updateOrderStatus(o.id, e.target.value);
                      refetch();
                    }}
                    className="rounded border border-border bg-card px-2 py-1 text-xs"
                  >
                    {['PENDING', 'PAYMENT_PENDING', 'PAID', 'CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'REFUNDED'].map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
};

export const AdminPaymentsPage: React.FC = () => {
  const { data: payments, refetch } = useQuery({ queryKey: ['admin-payments'], queryFn: adminApi.getPayments });

  return (
    <div className="space-y-6">
      <h1 className="font-serif text-3xl font-bold">Payment Management</h1>
      <Card className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-border text-xs text-muted-fg">
              <th className="py-2">Provider</th><th>Method</th><th>Status</th><th>Amount</th><th>Action</th>
            </tr>
          </thead>
          <tbody>
            {payments?.map((p: { id: string; provider: string; method: string; status: string; amount: string }) => (
              <tr key={p.id} className="border-b border-border/60">
                <td className="py-2">{p.provider}</td>
                <td>{p.method}</td>
                <td><Badge tone={p.status === 'PAID' ? 'success' : 'neutral'}>{p.status}</Badge></td>
                <td className="font-mono">${Number(p.amount).toFixed(2)}</td>
                <td>
                  {p.status === 'PAID' && (
                    <Button variant="outline" onClick={async () => { await adminApi.refundPayment(p.id, 'Admin refund'); refetch(); }}>
                      Refund
                    </Button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
};

export const AdminCustomersPage: React.FC = () => {
  const { user } = useAuthStore();
  const { data: users, refetch } = useQuery({ queryKey: ['admin-customers'], queryFn: adminApi.getCustomers });
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');

  return (
    <div className="space-y-6">
      <h1 className="font-serif text-3xl font-bold">Customers &amp; Admin Accounts</h1>
      {user?.role === 'super_admin' && (
        <Card>
          <h2 className="mb-3 text-sm font-semibold">Super Admin: Create Admin Account</h2>
          <form
            onSubmit={async (e) => {
              e.preventDefault();
              await adminApi.createAdminUser({ email, full_name: fullName, password, role_name: 'admin' });
              setEmail('');
              setFullName('');
              setPassword('');
              refetch();
            }}
            className="grid gap-3 sm:grid-cols-4"
          >
            <input required type="email" placeholder="Admin email" value={email} onChange={(e) => setEmail(e.target.value)} className="rounded-lg border border-border px-3 py-2 text-sm" />
            <input required placeholder="Full name" value={fullName} onChange={(e) => setFullName(e.target.value)} className="rounded-lg border border-border px-3 py-2 text-sm" />
            <input required type="password" minLength={8} placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} className="rounded-lg border border-border px-3 py-2 text-sm" />
            <Button type="submit">Create Admin</Button>
          </form>
        </Card>
      )}
      <Card className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead><tr className="border-b border-border text-xs text-muted-fg"><th className="py-2">Name</th><th>Email</th><th>Role</th><th>Status</th></tr></thead>
          <tbody>
            {users?.map((u) => (
              <tr key={u.id} className="border-b border-border/60">
                <td className="py-2">{u.full_name}</td>
                <td className="font-mono text-xs">{u.email}</td>
                <td><Badge tone="blush">{u.role}</Badge></td>
                <td>{u.is_active ? 'Active' : 'Disabled'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
};

export const AdminPromotionsCouponsPage: React.FC = () => {
  const { data: coupons, refetch } = useQuery({ queryKey: ['admin-coupons'], queryFn: adminApi.getCoupons });
  const [title, setTitle] = useState('');
  const [code, setCode] = useState('');
  const [val, setVal] = useState('15');

  return (
    <div className="space-y-6">
      <h1 className="font-serif text-3xl font-bold">Promotions &amp; Coupons</h1>
      <Card>
        <form
          onSubmit={async (e) => {
            e.preventDefault();
            const now = new Date();
            const end = new Date(now.getTime() + 30 * 86400000);
            await adminApi.createPromotion({
              title,
              discount_type: 'PERCENTAGE',
              discount_value: val,
              starts_at: now.toISOString(),
              ends_at: end.toISOString(),
              coupon_code: code,
            });
            setTitle('');
            setCode('');
            refetch();
          }}
          className="grid gap-3 sm:grid-cols-4"
        >
          <input required placeholder="Promotion title" value={title} onChange={(e) => setTitle(e.target.value)} className="rounded-lg border border-border px-3 py-2 text-sm" />
          <input required placeholder="Coupon code" value={code} onChange={(e) => setCode(e.target.value)} className="rounded-lg border border-border px-3 py-2 font-mono text-sm uppercase" />
          <input required type="number" min={1} max={90} value={val} onChange={(e) => setVal(e.target.value)} className="rounded-lg border border-border px-3 py-2 text-sm font-mono" />
          <Button type="submit">Create Promo</Button>
        </form>
      </Card>
      <div className="grid gap-3 sm:grid-cols-3">
        {coupons?.map((c: { id: string; code: string; discount_value: string; used_count: number }) => (
          <Card key={c.id}><div className="font-mono font-bold">{c.code}</div><div className="text-xs text-muted-fg">{c.discount_value}% off · Used {c.used_count} times</div></Card>
        ))}
      </div>
    </div>
  );
};

export const AdminReviewsPage: React.FC = () => {
  const { data: reviews, refetch } = useQuery({ queryKey: ['admin-reviews'], queryFn: adminApi.getReviews });

  return (
    <div className="space-y-4">
      <h1 className="font-serif text-3xl font-bold">Review Moderation</h1>
      {reviews?.map((r) => (
        <Card key={r.id} className="flex items-center justify-between gap-4">
          <div>
            <div className="font-semibold">{r.author_name} · {r.rating}/5</div>
            <p className="text-sm text-muted-fg">{r.comment}</p>
          </div>
          <Button variant="outline" onClick={async () => { await adminApi.moderateReview(r.id, !r.is_approved); refetch(); }}>
            {r.is_approved ? 'Hide' : 'Approve'}
          </Button>
        </Card>
      ))}
    </div>
  );
};

export const AdminMessagesPage: React.FC = () => {
  const { data: messages, refetch } = useQuery({ queryKey: ['admin-messages'], queryFn: engagementApi.listMessages });
  const [replyText, setReplyText] = useState<Record<string, string>>({});

  return (
    <div className="space-y-4">
      <h1 className="font-serif text-3xl font-bold">Customer Support Messages</h1>
      {messages?.map((m) => (
        <Card key={m.id} className="space-y-3">
          <div className="flex justify-between">
            <strong>{m.subject} ({m.customer_email})</strong>
            <Badge tone="blush">{m.status}</Badge>
          </div>
          <p className="text-sm">{m.message}</p>
          <div className="flex gap-2">
            <input
              placeholder="Write reply..."
              value={replyText[m.id] || ''}
              onChange={(e) => setReplyText((prev) => ({ ...prev, [m.id]: e.target.value }))}
              className="flex-1 rounded-lg border border-border px-3 py-2 text-sm"
            />
            <Button
              onClick={async () => {
                if (!replyText[m.id]) return;
                await adminApi.replyMessage(m.id, replyText[m.id]);
                setReplyText((prev) => ({ ...prev, [m.id]: '' }));
                refetch();
              }}
            >
              Send Reply
            </Button>
          </div>
        </Card>
      ))}
    </div>
  );
};

export const AdminNotificationsReportsSettingsPages = {
  Notifications: (() => {
    const Comp: React.FC = () => {
      const { data } = useQuery({ queryKey: ['notifications'], queryFn: engagementApi.listNotifications });
      return (
        <div className="space-y-4">
          <h1 className="font-serif text-3xl font-bold">Admin Notifications</h1>
          {data?.map((n) => (
            <Card key={n.id}><strong>{n.title}</strong><p className="text-sm text-muted-fg">{n.body}</p></Card>
          ))}
        </div>
      );
    };
    return Comp;
  })(),
  Reports: (() => {
    const Comp: React.FC = () => {
      const base = API_BASE_URL;
      return (
        <Card className="space-y-4">
          <h1 className="font-serif text-3xl font-bold">Export Reports</h1>
          <div className="flex flex-wrap gap-3">
            <a href={`${base}/admin/reports/export?report_type=sales`} className="touch-target inline-flex items-center rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white">
              Download Sales CSV
            </a>
            <a href={`${base}/admin/reports/export?report_type=inventory`} className="touch-target inline-flex items-center rounded-lg border border-border px-4 py-2 text-sm font-medium">
              Download Inventory CSV
            </a>
          </div>
        </Card>
      );
    };
    return Comp;
  })(),
  Settings: (() => {
    const Comp: React.FC = () => {
      const { user } = useAuthStore();
      const { data: settings } = useQuery({ queryKey: ['admin-settings'], queryFn: adminApi.getSettings });
      const { data: logs } = useQuery({
        queryKey: ['admin-audit-logs'],
        queryFn: adminApi.getAuditLogs,
        enabled: user?.role === 'super_admin',
      });
      return (
        <div className="space-y-6">
          <h1 className="font-serif text-3xl font-bold">System Settings &amp; Audit Logs</h1>
          <Card>
            <pre className="overflow-x-auto font-mono text-xs">{JSON.stringify(settings, null, 2)}</pre>
          </Card>
          {user?.role === 'super_admin' && (
            <Card className="space-y-2">
              <h2 className="font-semibold">Super Admin Audit Logs</h2>
              {logs?.slice(0, 20).map((l: { id: string; action: string; resource_type: string; created_at: string }) => (
                <div key={l.id} className="flex justify-between border-b border-border/50 py-1 font-mono text-xs">
                  <span>{l.action} ({l.resource_type})</span>
                  <span>{l.created_at}</span>
                </div>
              ))}
            </Card>
          )}
        </div>
      );
    };
    return Comp;
  })(),
};

