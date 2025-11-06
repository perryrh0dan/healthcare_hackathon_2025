import "./App.css";
import { Outlet } from '@tanstack/react-router';

function App() {
  return (
    <div
      style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}
    >
        <main style={{ flex: 1, padding: "2rem" }}>
           <Outlet />
         </main>
    </div>
  );
}

export default App;
