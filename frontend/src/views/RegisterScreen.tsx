import { Input } from '@/components/ui/input';
import { Button } from '../components/ui/button';

const RegisterScreen = () => {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="flex flex-col items-center rounded-md bg-white p-4">
        <h1 className="mb-8 text-center text-2xl font-bold">Register</h1>
        <form className="w-full max-w-sm space-y-4">
          <Input
            type="text"
            placeholder="Name"
          />
          <Input
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
