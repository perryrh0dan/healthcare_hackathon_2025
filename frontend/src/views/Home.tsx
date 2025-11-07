import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Link } from '@tanstack/react-router';
import { ChevronDown } from 'lucide-react';
import Message from '../components/ui/message';

const Home = () => {
  const { user } = useAuth();
  const [message, setMessage] = useState('');
  const [showTop, setShowTop] = useState(true);
  const [messages, setMessages] = useState<
    { text: string; sender: 'user' | 'bot' }[]
  >([]);

  const handleSend = () => {
    if (message.trim()) {
      setMessages((prev) => [...prev, { text: message, sender: 'user' }]);
      setMessage('');
      setShowTop(false);
    }
  };

  return (
    <div className="relative min-h-screen p-8">
      {!showTop && (
        <Button
          onClick={() => setShowTop(true)}
          className="fixed top-[70px] left-1/2 z-10 flex h-10 w-10 -translate-x-1/2 transform items-center justify-center rounded-full p-0"
        >
          <ChevronDown size={20} />
        </Button>
      )}

      <div className={`mb-8 ${showTop ? 'opacity-100' : 'opacity-0'}`}>
        <p className="text-gray-800">Welcome {user?.username}!</p>
        <div className="mt-4 grid grid-cols-2 gap-4">
          <div className="rounded-lg bg-green-100 p-4 shadow-lg">
            <h3 className="mb-2 text-lg font-semibold">Health Goals</h3>
            <p>Steps: 10,000 | Water: 8 glasses</p>
          </div>
          <div className="rounded-lg bg-cyan-100 p-4 shadow-lg">
            <h3 className="mb-2 text-lg font-semibold">Food Calendar</h3>
            <Link to="/calendar">
              <Button className="w-full bg-cyan-600 hover:bg-cyan-700">
                Go to Calendar
              </Button>
            </Link>
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
            <h3 className="mb-2 text-lg font-semibold">
              Upcoming Appointments
            </h3>
            <p>No upcoming appointments</p>
          </div>
        </div>
      </div>

      <div className="mb-20 flex-1 overflow-y-auto px-4">
        {messages.map((msg, index) => (
          <Message key={index} text={msg.text} sender={msg.sender} />
        ))}
      </div>

      <div className="fixed right-0 bottom-0 left-0 flex gap-2 border-t border-gray-300 bg-white p-4">
        <Input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type a message..."
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          className="flex-1"
        />
        <Button onClick={handleSend}>Send</Button>
      </div>
    </div>
  );
};

export default Home;
