import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { adminApi } from '@/services/api';
import { Badge, Button, Card } from '@/components/common/UI';

export const AdminInventoryPage: React.FC = () => {
  const { data: items, refetch } = useQuery({
    queryKey: ['admin-inventory'],
    queryFn: adminApi.getInventory,
  });
  const [variantId, setVariantId] = useState('');
  const [delta, setDelta] = useState(0);
  const [reason, setReason] = useState('');

  return (
    <div className="space-y-6">
      <h1 className="font-serif text-3xl font-bold">Inventory Management</h1>
      <Card>
        <form
          onSubmit={async (e) => {
            e.preventDefault();
            await adminApi.adjustInventory({
              variant_id: variantId || items?.[0]?.variant_id || '',
              quantity_delta: Number(delta),
              reason,
            });
            setReason('');
            refetch();
          }}
          className="grid gap-3 sm:grid-cols-4"
        >
          <select value={variantId} onChange={(e) => setVariantId(e.target.value)} className="rounded-lg border border-border bg-card px-3 py-2 text-sm">
            {items?.map((i) => <option key={i.variant_id} value={i.variant_id}>{i.sku} — {i.product_name}</option>)}
          </select>
          <input type="number" required placeholder="Qty Delta (+/-)" value={delta} onChange={(e) => setDelta(Number(e.target.value))} className="rounded-lg border border-border px-3 py-2 text-sm font-mono" />
          <input required minLength={3} placeholder="Audit Reason" value={reason} onChange={(e) => setReason(e.target.value)} className="rounded-lg border border-border px-3 py-2 text-sm" />
          <Button type="submit">Adjust Stock</Button>
        </form>
      </Card>

      <Card className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-border text-xs text-muted-fg">
              <th className="py-2">SKU</th><th>Product</th><th>Variant</th><th>Available</th><th>Reserved</th><th>Sellable</th><th>Alert</th>
            </tr>
          </thead>
          <tbody>
            {items?.map((i) => (
              <tr key={i.variant_id} className="border-b border-border/60">
                <td className="py-2 font-mono text-xs">{i.sku}</td>
                <td>{i.product_name}</td>
                <td>{i.variant_label}</td>
                <td className="font-mono">{i.available_quantity}</td>
                <td className="font-mono">{i.reserved_quantity}</td>
                <td className="font-mono font-bold">{i.sellable_quantity}</td>
                <td>
                  {i.is_out_of_stock ? <Badge tone="danger">Out of Stock</Badge> : i.is_low_stock ? <Badge tone="warning">Low Stock</Badge> : <Badge tone="success">Healthy</Badge>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
};

export const AdminBatchesExpiryPage: React.FC = () => {
  const { data: items } = useQuery({ queryKey: ['admin-inventory'], queryFn: adminApi.getInventory });
  const { data: expiring, refetch } = useQuery({ queryKey: ['admin-expiring'], queryFn: adminApi.getExpiring });

  const [variantId, setVariantId] = useState('');
  const [batchNumber, setBatchNumber] = useState('');
  const [mfgDate, setMfgDate] = useState('');
  const [expDate, setExpDate] = useState('');
  const [qty, setQty] = useState(10);

  return (
    <div className="space-y-6">
      <h1 className="font-serif text-3xl font-bold">Batches &amp; FEFO Expiry Tracking</h1>
      <Card>
        <form
          onSubmit={async (e) => {
            e.preventDefault();
            await adminApi.receiveBatch({
              variant_id: variantId || items?.[0]?.variant_id || '',
              batch_number: batchNumber,
              manufacture_date: mfgDate,
              expiry_date: expDate,
              quantity: qty,
            });
            setBatchNumber('');
            refetch();
          }}
          className="grid gap-3 sm:grid-cols-3"
        >
          <select value={variantId} onChange={(e) => setVariantId(e.target.value)} className="rounded-lg border border-border bg-card px-3 py-2 text-sm">
            {items?.map((i) => <option key={i.variant_id} value={i.variant_id}>{i.sku} — {i.product_name}</option>)}
          </select>
          <input required placeholder="Batch #" value={batchNumber} onChange={(e) => setBatchNumber(e.target.value)} className="rounded-lg border border-border px-3 py-2 text-sm font-mono" />
          <input required type="number" min={1} value={qty} onChange={(e) => setQty(Number(e.target.value))} className="rounded-lg border border-border px-3 py-2 text-sm font-mono" />
          <input required type="date" aria-label="Manufacture date" value={mfgDate} onChange={(e) => setMfgDate(e.target.value)} className="rounded-lg border border-border px-3 py-2 text-sm" />
          <input required type="date" aria-label="Expiry date" value={expDate} onChange={(e) => setExpDate(e.target.value)} className="rounded-lg border border-border px-3 py-2 text-sm" />
          <Button type="submit">Receive Batch</Button>
        </form>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="space-y-3">
          <h2 className="font-semibold text-destructive">Expired Batches (Blocked from Sale)</h2>
          {expiring?.expired?.map((b: { id: string; batch_number: string; product_name: string; expiry_date: string; remaining_quantity: number }) => (
            <div key={b.id} className="flex justify-between text-xs border-b border-border pb-2">
              <span>{b.product_name} ({b.batch_number})</span>
              <span className="font-mono">{b.expiry_date} · Qty {b.remaining_quantity}</span>
            </div>
          ))}
        </Card>
        <Card className="space-y-3">
          <h2 className="font-semibold text-amber-800">Expiring Within 60 Days</h2>
          {expiring?.expiring_soon?.map((b: { id: string; batch_number: string; product_name: string; expiry_date: string; remaining_quantity: number }) => (
            <div key={b.id} className="flex justify-between text-xs border-b border-border pb-2">
              <span>{b.product_name} ({b.batch_number})</span>
              <span className="font-mono">{b.expiry_date} · Qty {b.remaining_quantity}</span>
            </div>
          ))}
        </Card>
      </div>
    </div>
  );
};

