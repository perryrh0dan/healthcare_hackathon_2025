import { Button } from '../components/ui/button';
import { Link } from '@tanstack/react-router';
import { Input } from "../components/ui/input";
import { useMutation } from '@tanstack/react-query';

const LoginScreen = () => {
  const { mutate: login } = useMutation({
    mutationKey: ['login'],
    mutationFn: async (data: { username: string, password: string}) => {
      const response = await fetch(`http://localhost:8008/users/login`, { 
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });
      if (!response.ok) {
        throw new Error('Failed to fetch daily questions');
      }
    },
  });

  const handleSubmit = (event: any) => {
    event?.preventDefault();
    if (!event?.target) {
      return
    }

    const formData = new FormData(event.target as HTMLFormElement); // e.target = the form
    const data = Object.fromEntries(formData); // convert to plain object

    login({ username: data.username.toString(), password: data.password.toString()})
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
          <Button type="submit" className="w-full">
            Login
          </Button>
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
