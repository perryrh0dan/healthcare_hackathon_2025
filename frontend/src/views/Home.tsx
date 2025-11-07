 import { useState } from 'react';
 import { useAuth } from '../contexts/AuthContext';
 import { Link } from '@tanstack/react-router';
 import Chat from '../components/chat/Chat';
 import useAuthedQuery from '@/hooks/useAuthedQuery';
 import { Calendar, Cog, FlameIcon, Notebook, UserIcon } from 'lucide-react';

type Widget = {
  title: string
  type: "text" | "streak"
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
    <div className="flex flex-col gap-4 text-[#545454]">
      <div className='grid grid-cols-[1fr_auto] items-center'>
        <h1 className="text-2xl font-medium inline-flex">
          Weekly Recap
        </h1>
        <UserIcon className='border border-border rounded-full p-1 w-12 h-12' size={30} />
      </div>
      <div
        className={`grow transition-all duration-500 grid grid-cols-2 gap-4 ${showTop === false ? 'max-h-1' : ''}`}
      >
        <div className="col-span-2 rounded-lg bg-[#f5f5f5] p-6 shadow-sm relative">
          <h3 className="text-lg font-semibold">
            Welcome back {user?.first_name}!
          </h3>
        </div>
        <div className="col-span-2 grid grid-cols-4 gap-4">
          <Link className="rounded-lg bg-purple-100 p-4 shadow-lg flex justify-center items-center" to="/food-planner">
            <Calendar size={40} />
          </Link>
          <Link className="rounded-lg bg-purple-100 p-4 shadow-lg flex justify-center items-center" to="/daily">
            <Notebook size={40} />
          </Link>
          <Link className="rounded-lg bg-purple-100 p-4 shadow-lg flex justify-center items-center" to="/setup">
            <Cog size={40} />
          </Link>
        </div>
        { widgets?.map((w, idx) => { 
          if (w.type === 'text') {
            return (
              <div key={idx} className="rounded-lg bg-[#f5f5f5] p-6 shadow-sm h-40">
                <h3 className="mb-2 text-lg font-bold">{w.title}</h3>
                <p>{w.body}</p>
              </div>
            ) 
          } else if (w.type === 'streak') {
            return (
              <div key={idx} className="relative rounded-lg bg-[#f5f5f5] p-6 shadow-sm h-40">
                <h3 className="mb-2 text-lg font-bold">{w.title}</h3>
                <p className='left-5 bottom-5 absolute text-6xl font-bold'>{w.body}</p>
                <FlameIcon className="absolute right-1 bottom-3 text-amber-500 fill-amber-500" size={60} />
              </div>
            )
          } else {
            return (
              <Link to="/food-planner">
                <div key={idx} className="rounded-lg bg-[#f5f5f5] p-6 shadow-sm h-40">
                  <h3 className="mb-2 text-lg font-bold">{w.title}</h3>
                  <p>{w.body}</p>
                </div>
              </Link>
            )
           }
         })
        }
      </div>
      <div className="mb-14">
        <Chat open={!showTop} onSend={handleChatSend} onClose={() => setShowTop(true)} onOpen={() => setShowTop(false)} />
      </div>
    </div>
  );
};

export default Home;
