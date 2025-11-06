import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Link } from '@tanstack/react-router';

const Home = () => {
  const { user, logout } = useAuth();

  return (
    <div style={{ padding: '2rem' }}>
      <h1>Welcome, {user?.username}!</h1>
      <p>You are now logged in to the Healthcare App.</p>
      <div style={{ marginTop: '2rem' }}>
        <Link to="/daily">
          <Button style={{ marginRight: '1rem' }}>Daily Questions</Button>
        </Link>
        <Button onClick={logout} variant="outline">Logout</Button>
      </div>
    </div>
  );
};

export default Home;
