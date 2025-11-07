import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Link } from '@tanstack/react-router';
import { ChevronDown, ChevronUp } from 'lucide-react';
import Chat from '../components/chat/Chat';

const Home = () => {
  const { user } = useAuth();
  const [showTop, setShowTop] = useState(true);

  return (
    <div className="relative min-h-screen w-100">
      <Button
        onClick={() => setShowTop(!showTop)}
        className="fixed top-[70px] left-1/2 z-10 flex h-10 w-10 -translate-x-1/2 transform items-center justify-center rounded-full p-0"
      >
        {showTop ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
      </Button>

      <div
        className={`mb-8 transition-all duration-500 ${
          showTop
            ? 'visible block opacity-100'
            : 'hidden max-h-0 overflow-hidden'
        } rounded-lg p-3 shadow-lg`}
      >
        <div className="col-span-2 rounded-lg bg-rose-100 p-4 shadow-lg">
          <h3 className="mb-2 text-lg font-semibold">
            Welcome {user?.username}!
          </h3>
        </div>
        <div className="mt-4 grid grid-cols-2 gap-4">
          <div className="rounded-lg bg-green-100 p-4 shadow-lg">
            <h3 className="mb-2 text-lg font-semibold">Health Goals</h3>
            <p>Steps: 10,000 | Water: 8 glasses</p>
          </div>
          <div className="rounded-lg bg-cyan-100 p-4 shadow-lg">
            <h3 className="mb-2 text-lg font-semibold">Food Calendar</h3>
            <p>Coming soon</p>
          </div>
          <div className="rounded-lg bg-teal-100 p-4 shadow-lg">
            <h3 className="mb-2 text-lg font-semibold">Daily Questions</h3>
            <Link to="/daily">
              <Button className="w-full bg-teal-600 hover:bg-teal-700">
                Go to Questions
              </Button>
            </Link>
          </div>
          <div className="rounded-lg bg-blue-50 p-4 shadow-lg">
            <h3 className="mb-2 text-lg font-semibold">Recent Activity</h3>
            <p>Logged in today</p>
          </div>
          <div className="rounded-lg bg-orange-100 p-4 shadow-lg">
            <h3 className="mb-2 text-lg font-semibold">Appointments</h3>
            <p>No upcoming appointments</p>
          </div>
          <div className="rounded-lg bg-purple-100 p-4 shadow-lg">
            <h3 className="mb-2 text-lg font-semibold">Setup</h3>
            <Link to="/setup">
              <Button className="w-full bg-purple-600 hover:bg-purple-700">
                Go to Setup
              </Button>
            </Link>
          </div>
        </div>
      </div>

      <div className="flex-1">
        <Chat />
      </div>
    </div>
  );
};

export default Home;
