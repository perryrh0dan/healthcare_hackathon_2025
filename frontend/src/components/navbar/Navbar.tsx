import { Link } from '@tanstack/react-router';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../ui/button';
import logo from '../../assets/logo-erlangen.png';

const Navbar = () => {
  const { logout } = useAuth();

  return (
    <header className="bg-primary text-primary-foreground p-4 shadow-md">
      <div className="container mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link to="/">
            <img src={logo} alt="Erlangen Logo" className="h-10 w-auto" />
          </Link>
          <h1 className="text-xl font-semibold">Healthcare Dashboard</h1>
        </div>
        <Button onClick={logout} variant="outline" style={{ color: '#333' }}>
          Logout
        </Button>
      </div>
    </header>
  );
};

export default Navbar;
