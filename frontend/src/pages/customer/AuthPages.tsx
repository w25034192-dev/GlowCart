import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authApi } from '@/services/api';
import { useAuthStore } from '@/store/authStore';
import { useCartStore } from '@/store/cartStore';
import { AlertBox, Button, Card } from '@/components/common/UI';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { setSession } = useAuthStore();
  const { fetchCart } = useCartStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await authApi.login({ email, password });
      setSession(data.access_token, data.refresh_token, data.user);
      await fetchCart();
      navigate(data.user.role === 'customer' ? '/' : '/admin');
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg || 'Invalid email or password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-md py-6">
      <Card className="space-y-5">
        <div>
          <h1 className="font-serif text-3xl font-bold">Welcome Back</h1>
          <p className="mt-1 text-sm text-muted-fg">Sign in to your GlowCart account.</p>
        </div>
        {error && <AlertBox message={error} />}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="login-email" className="block text-sm font-medium">
              Email
            </label>
            <input
              id="login-email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-lg border border-border px-3 py-2.5 text-sm"
            />
          </div>
          <div>
            <label htmlFor="login-password" className="block text-sm font-medium">
              Password
            </label>
            <input
              id="login-password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-lg border border-border px-3 py-2.5 text-sm"
            />
          </div>
          <Button type="submit" disabled={loading} className="w-full">
            {loading ? 'Signing in...' : 'Sign In'}
          </Button>
        </form>
        <div className="flex justify-between text-xs text-muted-fg">
          <Link to="/forgot-password" className="text-primary hover:underline">
            Forgot password?
          </Link>
          <Link to="/register" className="text-primary hover:underline">
            Create an account
          </Link>
        </div>
      </Card>
    </div>
  );
};

export const RegisterPage: React.FC = () => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await authApi.register({ full_name: fullName, email, phone: phone || undefined, password });
      navigate('/login');
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-md py-6">
      <Card className="space-y-5">
        <div>
          <h1 className="font-serif text-3xl font-bold">Create Account</h1>
          <p className="mt-1 text-sm text-muted-fg">Join GlowCart for personalized beauty shopping.</p>
        </div>
        {error && <AlertBox message={error} />}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="reg-name" className="block text-sm font-medium">
              Full Name
            </label>
            <input
              id="reg-name"
              type="text"
              required
              minLength={2}
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="mt-1 w-full rounded-lg border border-border px-3 py-2.5 text-sm"
            />
          </div>
          <div>
            <label htmlFor="reg-email" className="block text-sm font-medium">
              Email
            </label>
            <input
              id="reg-email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-lg border border-border px-3 py-2.5 text-sm"
            />
          </div>
          <div>
            <label htmlFor="reg-phone" className="block text-sm font-medium">
              Phone (Optional)
            </label>
            <input
              id="reg-phone"
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="mt-1 w-full rounded-lg border border-border px-3 py-2.5 text-sm"
            />
          </div>
          <div>
            <label htmlFor="reg-password" className="block text-sm font-medium">
              Password (min 8 chars)
            </label>
            <input
              id="reg-password"
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-lg border border-border px-3 py-2.5 text-sm"
            />
          </div>
          <Button type="submit" disabled={loading} className="w-full">
            {loading ? 'Creating account...' : 'Register'}
          </Button>
        </form>
        <p className="text-center text-xs text-muted-fg">
          Already registered?{' '}
          <Link to="/login" className="text-primary hover:underline">
            Sign in
          </Link>
        </p>
      </Card>
    </div>
  );
};

export const ForgotPasswordPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [resetToken, setResetToken] = useState('');
  const [newPassword, setNewPassword] = useState('');

  const handleRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await authApi.forgotPassword(email);
    setMessage(res.message);
    if (res.reset_token) setResetToken(res.reset_token);
  };

  const handleReset = async (e: React.FormEvent) => {
    e.preventDefault();
    await authApi.resetPassword({ token: resetToken, new_password: newPassword });
    setMessage('Password updated! You may now sign in.');
  };

  return (
    <div className="mx-auto max-w-md space-y-6 py-6">
      <Card className="space-y-4">
        <h1 className="font-serif text-3xl font-bold">Reset Password</h1>
        {message && <AlertBox message={message} tone="info" />}
        <form onSubmit={handleRequest} className="space-y-3">
          <label htmlFor="fp-email" className="block text-sm font-medium">
            Account Email
          </label>
          <input
            id="fp-email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-lg border border-border px-3 py-2.5 text-sm"
          />
          <Button type="submit" className="w-full">
            Request Reset Token
          </Button>
        </form>

        <form onSubmit={handleReset} className="space-y-3 border-t border-border pt-4">
          <label htmlFor="fp-token" className="block text-sm font-medium">
            Reset Token
          </label>
          <input
            id="fp-token"
            type="text"
            required
            value={resetToken}
            onChange={(e) => setResetToken(e.target.value)}
            className="w-full rounded-lg border border-border px-3 py-2.5 font-mono text-xs"
          />
          <label htmlFor="fp-newpw" className="block text-sm font-medium">
            New Password
          </label>
          <input
            id="fp-newpw"
            type="password"
            required
            minLength={8}
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            className="w-full rounded-lg border border-border px-3 py-2.5 text-sm"
          />
          <Button type="submit" variant="secondary" className="w-full">
            Confirm Password Reset
          </Button>
        </form>
      </Card>
    </div>
  );
};

