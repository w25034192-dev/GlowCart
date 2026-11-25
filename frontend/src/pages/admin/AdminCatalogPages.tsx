import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { adminApi, catalogApi } from '@/services/api';
import { Badge, Button, Card } from '@/components/common/UI';

export const AdminProductsPage: React.FC = () => {
  const { data: products, refetch } = useQuery({
    queryKey: ['admin-products'],
    queryFn: () => catalogApi.getProducts({ page_size: 50 }),
  });
  const { data: categories } = useQuery({ queryKey: ['categories'], queryFn: catalogApi.getCategories });
  const { data: brands } = useQuery({ queryKey: ['brands'], queryFn: catalogApi.getBrands });

  const [name, setName] = useState('');
  const [slug, setSlug] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [brandId, setBrandId] = useState('');
  const [description, setDescription] = useState('');

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    await adminApi.createProduct({
      name,
      slug: slug || name.toLowerCase().replace(/\s+/g, '-'),
      category_id: categoryId || categories?.[0]?.id,
      brand_id: brandId || brands?.[0]?.id,
      description,
    });
    setName('');
    setSlug('');
    setDescription('');
    refetch();
  };

  return (
    <div className="space-y-6">
      <h1 className="font-serif text-3xl font-bold">Product Management</h1>
      <Card>
        <form onSubmit={handleCreate} className="grid gap-3 sm:grid-cols-2">
          <input required placeholder="Product name" value={name} onChange={(e) => setName(e.target.value)} className="rounded-lg border border-border px-3 py-2 text-sm" />
          <input placeholder="Slug (auto if empty)" value={slug} onChange={(e) => setSlug(e.target.value)} className="rounded-lg border border-border px-3 py-2 text-sm" />
          <select value={categoryId} onChange={(e) => setCategoryId(e.target.value)} className="rounded-lg border border-border bg-card px-3 py-2 text-sm">
            {categories?.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          <select value={brandId} onChange={(e) => setBrandId(e.target.value)} className="rounded-lg border border-border bg-card px-3 py-2 text-sm">
            {brands?.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
          </select>
          <textarea required placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} className="sm:col-span-2 rounded-lg border border-border px-3 py-2 text-sm" />
          <Button type="submit" className="sm:col-span-2">Create Product</Button>
        </form>
      </Card>
      <Card className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead><tr className="border-b border-border text-xs text-muted-fg"><th className="py-2">Product</th><th>Brand</th><th>Category</th><th>Price</th><th>Stock</th></tr></thead>
          <tbody>
            {products?.items.map((p) => (
              <tr key={p.id} className="border-b border-border/60">
                <td className="py-2 font-medium">{p.name}</td>
                <td>{p.brand_name}</td>
                <td>{p.category_name}</td>
                <td className="font-mono">${Number(p.min_price || 0).toFixed(2)}</td>
                <td><Badge tone={p.in_stock ? 'success' : 'danger'}>{p.in_stock ? 'In Stock' : 'Out'}</Badge></td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
};

export const AdminCategoriesPage: React.FC = () => {
  const { data: categories, refetch } = useQuery({ queryKey: ['categories'], queryFn: catalogApi.getCategories });
  const [name, setName] = useState('');
  const [slug, setSlug] = useState('');

  return (
    <div className="space-y-6">
      <h1 className="font-serif text-3xl font-bold">Category Management</h1>
      <Card>
        <form
          onSubmit={async (e) => {
            e.preventDefault();
            await adminApi.createCategory({ name, slug: slug || name.toLowerCase().replace(/\s+/g, '-') });
            setName('');
            setSlug('');
            refetch();
          }}
          className="flex flex-wrap gap-3"
        >
          <input required placeholder="Category Name" value={name} onChange={(e) => setName(e.target.value)} className="rounded-lg border border-border px-3 py-2 text-sm" />
          <input placeholder="Slug" value={slug} onChange={(e) => setSlug(e.target.value)} className="rounded-lg border border-border px-3 py-2 text-sm" />
          <Button type="submit">Add Category</Button>
        </form>
      </Card>
      <div className="grid gap-3 sm:grid-cols-3">
        {categories?.map((c) => (
          <Card key={c.id}><div className="font-semibold">{c.name}</div><div className="text-xs font-mono text-muted-fg">{c.slug}</div></Card>
        ))}
      </div>
    </div>
  );
};

export const AdminBrandsPage: React.FC = () => {
  const { data: brands, refetch } = useQuery({ queryKey: ['brands'], queryFn: catalogApi.getBrands });
  const [name, setName] = useState('');
  const [country, setCountry] = useState('');

  return (
    <div className="space-y-6">
      <h1 className="font-serif text-3xl font-bold">Brand Management</h1>
      <Card>
        <form
          onSubmit={async (e) => {
            e.preventDefault();
            await adminApi.createBrand({ name, slug: name.toLowerCase().replace(/\s+/g, '-'), country_of_origin: country });
            setName('');
            setCountry('');
            refetch();
          }}
          className="flex flex-wrap gap-3"
        >
          <input required placeholder="Brand Name" value={name} onChange={(e) => setName(e.target.value)} className="rounded-lg border border-border px-3 py-2 text-sm" />
          <input placeholder="Country of Origin" value={country} onChange={(e) => setCountry(e.target.value)} className="rounded-lg border border-border px-3 py-2 text-sm" />
          <Button type="submit">Add Brand</Button>
        </form>
      </Card>
      <div className="grid gap-3 sm:grid-cols-3">
        {brands?.map((b) => (
          <Card key={b.id}><div className="font-semibold">{b.name}</div><div className="text-xs text-muted-fg">{b.country_of_origin}</div></Card>
        ))}
      </div>
    </div>
  );
};

export const AdminVariantsPage: React.FC = () => {
  const { data: products } = useQuery({
    queryKey: ['admin-products-list'],
    queryFn: () => catalogApi.getProducts({ page_size: 50 }),
  });
  const [productId, setProductId] = useState('');
  const [sku, setSku] = useState('');
  const [shadeName, setShadeName] = useState('');
  const [hexColor, setHexColor] = useState('');
  const [volumeMl, setVolumeMl] = useState('');
  const [price, setPrice] = useState('25.00');
  const [msg, setMsg] = useState('');

  return (
    <div className="space-y-6">
      <h1 className="font-serif text-3xl font-bold">Variant Management (Shades &amp; Volumes)</h1>
      <Card>
        <form
          onSubmit={async (e) => {
            e.preventDefault();
            await adminApi.createVariant({
              product_id: productId || products?.items[0]?.id,
              sku,
              shade_name: shadeName || null,
              hex_color: hexColor || null,
              volume_ml: volumeMl ? Number(volumeMl) : null,
              price,
            });
            setSku('');
            setMsg('Variant created!');
          }}
          className="grid gap-3 sm:grid-cols-2"
        >
          <select value={productId} onChange={(e) => setProductId(e.target.value)} className="rounded-lg border border-border bg-card px-3 py-2 text-sm">
            {products?.items.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
          <input required placeholder="SKU (e.g. MAC-001)" value={sku} onChange={(e) => setSku(e.target.value)} className="rounded-lg border border-border px-3 py-2 text-sm font-mono" />
          <input placeholder="Shade Name (optional)" value={shadeName} onChange={(e) => setShadeName(e.target.value)} className="rounded-lg border border-border px-3 py-2 text-sm" />
          <input placeholder="HEX Color" value={hexColor} onChange={(e) => setHexColor(e.target.value)} className="rounded-lg border border-border px-3 py-2 text-sm font-mono" />
          <input type="number" placeholder="Volume ml (optional)" value={volumeMl} onChange={(e) => setVolumeMl(e.target.value)} className="rounded-lg border border-border px-3 py-2 text-sm" />
          <input required placeholder="Price USD" value={price} onChange={(e) => setPrice(e.target.value)} className="rounded-lg border border-border px-3 py-2 text-sm font-mono" />
          <Button type="submit" className="sm:col-span-2">Create Variant</Button>
        </form>
        {msg && <p className="mt-2 text-xs text-accent">{msg}</p>}
      </Card>
    </div>
  );
};

