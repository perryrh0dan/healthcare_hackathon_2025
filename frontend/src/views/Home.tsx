import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Link } from '@tanstack/react-router';
import Chat from '../components/chat/Chat';
import useAuthedQuery from '@/hooks/useAuthedQuery';

type Widget = {
  title: string
  type: "text"
  body: string
}

const Home = () => {
  const { user } = useAuth();
  const [showTop, setShowTop] = useState(true);

  const { data: widgets } = useAuthedQuery({
    queryKey: ['widgets'],
    queryFn: async () => {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/dashboard/widgets`, { credentials: 'include' });
      if (!response.ok) {
        throw new Error('Failed to fetch daily questions');
      }
      return response.json() as Promise<Widget[]>;
    },
    initialData: []
  })

  const handleChatSend = () => {
    if (showTop) {
      setShowTop(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <h2 className='text-4xl font-semibold'>Weekly<br />Recap</h2>
      <div
        className={`grow transition-all duration-500 grid grid-cols-2 gap-4 ${showTop === false ? 'max-h-1' : ''}`}
      >
        <div className="col-span-2 rounded-lg bg-green-300 p-6 shadow-lg">
          <h3 className="text-lg font-semibold text-white">
            Welcome back {user?.first_name}!
          </h3>
        </div>
        { widgets?.map((w, idx) => (
          <div key={idx} className="rounded-lg bg-green-100 p-4 shadow-lg">
            <h3 className="mb-2 text-lg font-semibold">{w.title}</h3>
            <p>{w.body}</p>
          </div>
        ))}
        <Link  className="rounded-lg bg-cyan-100 p-4 shadow-lg" to="/food-planner">
          <h3 className="mb-2 text-lg font-semibold">Food Plan</h3>
        </Link>
        <Link className="rounded-lg bg-teal-100 p-4 shadow-lg" to="/daily">
          <h3 className="mb-2 text-lg font-semibold">Daily Questions</h3>
        </Link>
        <Link className="rounded-lg bg-purple-100 p-4 shadow-lg" to="/setup">
          <h3 className="mb-2 text-lg font-semibold">Setup</h3>
        </Link>
      </div>
      <div className="mb-14">
        <Chat open={!showTop} onSend={handleChatSend} onClose={() => setShowTop(true)} onOpen={() => setShowTop(false)} />
      </div>
    </div>
  );
};

export default Home;
