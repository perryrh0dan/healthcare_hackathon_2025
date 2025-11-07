import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Link } from '@tanstack/react-router';
import { ChevronDown, ChevronUp } from 'lucide-react';
import Chat from '../components/chat/Chat';

const Home = () => {
  const { user } = useAuth();
  const [showTop, setShowTop] = useState(true);

  const handleChatSend = () => {
    setShowTop(old => !old)
  }

  return (
    <div className="relative min-h-screen w-100">

      { showTop && ( <div
        className={`mb-8 transition-all duration-500 grid grid-cols-2 gap-4 ${
          showTop
            ? 'visible block opacity-100'
            : 'hidden max-h-0 overflow-hidden'
        } `}
      >
        <h2 className='text-4xl font-semibold'>Weekly<br />Recap</h2>
        <div className="col-span-2 rounded-lg bg-green-300 p-6 shadow-lg">
          <h3 className="text-lg font-semibold text-white">
            Welcome back {user?.first_name}!
          </h3>
        </div>
        <div className="rounded-lg bg-green-100 p-4 shadow-lg">
          <h3 className="mb-2 text-lg font-semibold">Health Goals</h3>
          <p>Steps: 10,000 | Water: 8 glasses</p>
        </div>
        <div className="rounded-lg bg-cyan-100 p-4 shadow-lg">
          <h3 className="mb-2 text-lg font-semibold">Food Calendar</h3>
          <p>Coming soon</p>
        </div>
        <div className="rounded-lg bg-teal-100 p-4 shadow-lg">
          <Link to="/daily">
            <h3 className="mb-2 text-lg font-semibold">Daily Questions</h3>
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
          <Link to="/setup">
            <h3 className="mb-2 text-lg font-semibold">Setup</h3>
          </Link>
        </div>
      </div> ) }
      <div className='h-10 w-full flex items-center justify-center'>
        <Button
          onClick={() => setShowTop(!showTop)}
          className="rounded-full"
        >
          {showTop ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </Button>
      </div>
      <div className="flex-1">
        <Chat open={!showTop} onSend={handleChatSend} />
      </div>
    </div>
  );
};

export default Home;
