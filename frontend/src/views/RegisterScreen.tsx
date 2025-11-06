import { Input } from '@/components/ui/input';
import { Button } from '../components/ui/button';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from '@tanstack/react-router';
import { useAuth } from '@/contexts';
import { useEffect } from 'react';

const RegisterScreen = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate()
 
  useEffect(() => {
    if (isAuthenticated) {
      navigate({ to: '/home' });
    }
  }, [isAuthenticated, navigate]);

  const { mutate: register } = useMutation({
    mutationKey: ['register-user'],
    mutationFn: async (user: { username: string, password: string}) => {
      const response = await fetch(`http://localhost:8008/users/register`, { 
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(user)
      });
      if (!response.ok) {
        throw new Error('Failed to fetch daily questions');
      }
    },
    onSuccess: () => {
      navigate({ to: '/login' })
    }
  });

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event?.preventDefault();
    if (!event?.target) {
      return
    }

    const formData = new FormData(event.target as HTMLFormElement); // e.target = the form
    const data = Object.fromEntries(formData); // convert to plain object

    register({ username: data.username.toString(), password: data.password.toString()})
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="flex flex-col items-center rounded-md bg-white p-4">
        <h1 className="mb-8 text-center text-2xl font-bold">Register</h1>
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
          <Button type="submit" className="h-12 w-full">
            Register
          </Button>
        </form>
      </div>
    </div>
  );
};

export default RegisterScreen;
