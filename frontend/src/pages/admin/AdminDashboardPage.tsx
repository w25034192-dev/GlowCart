import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { adminApi } from '@/services/api';
import { Card } from '@/components/common/UI';

const CHART_COLORS = [
  'var(--color-chart-1)',
  'var(--color-chart-2)',
  'var(--color-chart-3)',
  'var(--color-chart-4)',
  'var(--color-chart-5)',
];

export const AdminDashboardPage: React.FC = () => {
  const [granularity, setGranularity] = useState<'daily' | 'weekly' | 'monthly' | 'yearly'>('daily');

  const { data: overview } = useQuery({
    queryKey: ['admin-overview'],
    queryFn: adminApi.getOverview,
  });
  const { data: salesSeries } = useQuery({
    queryKey: ['admin-sales', granularity],
    queryFn: () => adminApi.getSalesSeries(granularity),
  });
  const { data: bestSellers } = useQuery({
    queryKey: ['admin-best-sellers'],
    queryFn: adminApi.getBestSellers,
  });
  const { data: categorySales } = useQuery({
    queryKey: ['admin-category-sales'],
    queryFn: adminApi.getCategorySales,
  });
  const { data: variantStats } = useQuery({
    queryKey: ['admin-variant-stats'],
    queryFn: adminApi.getVariantAnalytics,
  });
  const { data: inventoryStats } = useQuery({
    queryKey: ['admin-inventory-stats'],
    queryFn: adminApi.getInventoryAnalytics,
  });

  const kpis = [
    { label: 'Total Revenue', value: overview ? `$${overview.total_revenue.toFixed(2)}` : '$0.00' },
    { label: 'Total Orders', value: overview?.total_orders ?? 0 },
    { label: 'Total Customers', value: overview?.total_customers ?? 0 },
    { label: 'Total Products', value: overview?.total_products ?? 0 },
    { label: 'Pending Orders', value: overview?.pending_orders ?? 0 },
    { label: 'Low-Stock Variants', value: overview?.low_stock_products ?? 0 },
    { label: 'Out-of-Stock Variants', value: overview?.out_of_stock_products ?? 0 },
    { label: 'Near-Expiry / Expired Batches', value: overview?.near_expiry_batches ?? 0 },
  ];

  return (
    <div className="mx-auto max-w-[1400px] space-y-6">
      <div>
        <h1 className="font-serif text-3xl font-bold">Executive Dashboard &amp; Analytics</h1>
        <p className="text-sm text-muted-fg">
          Real-time SQL metrics calculated from database records (cancelled &amp; refunded revenue excluded).
        </p>
      </div>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {kpis.map((kpi) => (
          <Card key={kpi.label} className="p-4">
            <div className="text-xs font-semibold uppercase tracking-wide text-muted-fg">{kpi.label}</div>
            <div className="mt-2 font-mono text-2xl font-bold text-foreground">{kpi.value}</div>
          </Card>
        ))}
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <Card className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-serif text-xl font-bold">Revenue Trend</h2>
            <select
              aria-label="Revenue granularity"
              value={granularity}
              onChange={(e) => setGranularity(e.target.value as typeof granularity)}
              className="rounded-lg border border-border bg-card px-2.5 py-1.5 text-xs"
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
              <option value="yearly">Yearly</option>
            </select>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={salesSeries || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="period" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="revenue"
                  stroke="var(--color-primary)"
                  fill="var(--color-blush)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card className="space-y-4">
          <h2 className="font-serif text-xl font-bold">Sales by Category &amp; Brand</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categorySales?.by_category || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="revenue" fill="var(--color-primary)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card className="space-y-4">
          <h2 className="font-serif text-xl font-bold">Best-Selling Products &amp; Shades</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={bestSellers || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="product_name" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="units_sold" fill="var(--color-accent)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="grid gap-3 pt-2 text-xs sm:grid-cols-2">
            <div>
              <strong>Top Lipstick Shades:</strong>{' '}
              {variantStats?.lipstick_shades.slice(0, 3).map((s) => `${s.shade} (${s.units_sold})`).join(', ') || 'No sales yet'}
            </div>
            <div>
              <strong>Top Foundation Shades:</strong>{' '}
              {variantStats?.foundation_shades.slice(0, 3).map((s) => `${s.shade} (${s.units_sold})`).join(', ') || 'No sales yet'}
            </div>
          </div>
        </Card>

        <Card className="space-y-4">
          <h2 className="font-serif text-xl font-bold">Inventory Health &amp; Volume Breakdown</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={inventoryStats?.status_breakdown || []}
                  dataKey="count"
                  nameKey="status"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label
                >
                  {(inventoryStats?.status_breakdown || []).map((_: unknown, index: number) => (
                    <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </section>
    </div>
  );
};

