import { Button } from '../components/ui/button';
import { Link, useNavigate } from '@tanstack/react-router';
import { Input } from "../components/ui/input";
import { useAuth } from '../contexts/AuthContext';
import { useEffect, useState } from 'react';

const LoginScreen = () => {
  const { login: authLogin, isLoading, isAuthenticated } = useAuth();
  const [error, setError] = useState<string>('');
  const navigate = useNavigate();
  
  useEffect(() => {
    if (isAuthenticated) {
      navigate({ to: '/home' });
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event?.preventDefault();
    if (!event?.target) {
      return
    }

    const formData = new FormData(event.target as HTMLFormElement);
    const data = Object.fromEntries(formData);

    try {
      setError('');
      await authLogin(data.username.toString(), data.password.toString());
      navigate({ to: '/home' });
    } catch {
      setError('Login failed. Please check your credentials.');
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="flex flex-col items-center rounded-md bg-white p-4">
        <h1 className="mb-8 text-center text-2xl font-bold">Login</h1>
        <form className="w-full max-w-sm space-y-4" onSubmit={handleSubmit}>
          <Input
            name='username'
            type="text"
            placeholder="Name"
          />
          <Input
            name='password'
            type="password"
            placeholder="Password"
          />
          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? 'Logging in...' : 'Login'}
          </Button>
          {error && (
            <p className="text-red-500 text-sm mt-2">{error}</p>
          )}
        </form>
        <div className="mt-4 text-center w-full">
          <Link to="/register">
            <Button variant="outline" className="w-full">
              Register
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default LoginScreen;
