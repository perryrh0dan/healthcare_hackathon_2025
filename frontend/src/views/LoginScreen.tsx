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
     if (isAuthenticated && !isLoading) {
       navigate({ to: '/home' });
     }
   }, [isAuthenticated, isLoading, navigate]);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event?.preventDefault();
    if (!event?.target) {
      return;
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
  };

  return (
    <div className="w-full max-w-md flex h-full justify-center items-center grow">
      <div className="bg-card border-border flex flex-col items-center rounded-lg border p-6 shadow-lg">
        <h1 className="mb-8 text-center text-2xl font-bold">Login</h1>
        <form className="w-full max-w-sm space-y-4" onSubmit={handleSubmit}>
          <Input name="username" type="text" placeholder="Name" />
          <Input name="password" type="password" placeholder="Password" />
          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? 'Logging in...' : 'Login'}
          </Button>
          {error && <p className="mt-2 text-sm text-red-500">{error}</p>}
          <Link to="/register">
            <Button variant="outline" className="w-full">
              Register
            </Button>
          </Link>
        </form>
      </div>
    </div>
  );
};

export default LoginScreen;
