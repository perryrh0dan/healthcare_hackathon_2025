import "./App.css";
import { Outlet } from '@tanstack/react-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './contexts';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <div
          style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}
        >
            <main style={{ flex: 1, padding: "2rem" }}>
               <Outlet />
              </main>
        </div>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
