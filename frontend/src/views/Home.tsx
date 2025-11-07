import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Link } from '@tanstack/react-router';
import Chat from '../components/chat/Chat';

const Home = () => {
  const { user } = useAuth();
  const [showTop, setShowTop] = useState(true);

  const handleChatSend = () => {
    if (showTop) {
      setShowTop(false);
    }
  };

  return (
    <div className="flex min-h-screen w-100 flex-col gap-4">
      <h2 className="text-4xl font-semibold">
        Weekly
        <br />
        Recap
      </h2>
      <div className="grid grow grid-cols-2 gap-4 transition-all duration-500">
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
          <Link to="/food-planner">
            <h3 className="mb-2 text-lg font-semibold">Food Plan</h3>
          </Link>
        </div>
        <Link  className="rounded-lg bg-teal-100 p-4 shadow-lg" to="/daily">
          <div>
              <h3 className="mb-2 text-lg font-semibold">Daily Questions</h3>
          </div>
        </Link>
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
      </div>
      <div className="">
        <Chat
          open={!showTop}
          onSend={handleChatSend}
          onClose={() => setShowTop(true)}
          onOpen={() => setShowTop(false)}
        />
      </div>
    </div>
  );
};

export default Home;
