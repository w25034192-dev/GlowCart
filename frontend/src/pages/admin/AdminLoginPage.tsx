import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '@/services/api';
import { useAuthStore } from '@/store/authStore';
import { AlertBox, Button, Card } from '@/components/common/UI';

export const AdminLoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { setSession } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const data = await authApi.login({ email, password });
      if (data.user.role !== 'admin' && data.user.role !== 'super_admin') {
        setError('Access denied: Administrator credentials required.');
        return;
      }
      setSession(data.access_token, data.refresh_token, data.user);
      navigate('/admin');
    } catch {
      setError('Invalid administrator credentials.');
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md space-y-5">
        <div>
          <h1 className="font-serif text-3xl font-bold text-primary">GlowCart Admin</h1>
          <p className="mt-1 text-sm text-muted-fg">Sign in to manage catalog, inventory, and analytics.</p>
        </div>
        {error && <AlertBox message={error} />}
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            required
            placeholder="Admin email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-lg border border-border px-3 py-2.5 text-sm"
          />
          <input
            type="password"
            required
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-lg border border-border px-3 py-2.5 text-sm"
          />
          <Button type="submit" className="w-full">
            Sign In to Admin
          </Button>
        </form>
      </Card>
    </div>
  );
};

