import './App.css';
import { Outlet } from '@tanstack/react-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './contexts';
import Navbar from './components/navbar/Navbar';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <div
          style={{
            minHeight: '100vh',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <Navbar />
          <main className="flex flex-1 items-center justify-center p-4">
            <Outlet />
          </main>
        </div>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
