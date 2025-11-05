import "./App.css";
import Navbar from "./components/navbar/navbar";
import Footer from "./components/footer/footer";
import Chatbot from "./components/chatbot/chatbot";

function App() {
  return (
    <div
      style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}
    >
      <Navbar />
       <main style={{ flex: 1, padding: "2rem" }}>
          <Chatbot />
        </main>
      <Footer />
    </div>
  );
}

export default App;
