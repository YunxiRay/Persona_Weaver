import { Routes, Route } from "react-router-dom";
import Home from "@/pages/Home";
import Chat from "@/pages/Chat";
import Report from "@/pages/Report";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/chat" element={<Chat />} />
      <Route path="/report/:id" element={<Report />} />
    </Routes>
  );
}
