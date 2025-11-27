import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import "./App.css";
import Chat from "./pages/chat/chat";
import { Toaster } from "@/components/ui/sonner";

function App() {
  return (
    <>
      <Toaster richColors position="top-right" duration={7000} />
      <Router>
        <Routes>
          <Route path="/" element={<Chat />} />
        </Routes>
      </Router>
    </>
  );
}

export default App;
