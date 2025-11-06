import { Button } from '../components/ui/button';
import { Link } from '@tanstack/react-router';
import { Input } from "../components/ui/input";

const LoginScreen = () => {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="flex flex-col items-center rounded-md bg-white p-4">
        <h1 className="mb-8 text-center text-2xl font-bold">Login</h1>
        <form className="w-full max-w-sm space-y-4">
          <Input
            type="text"
            placeholder="Name"
          />
          <Input
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
