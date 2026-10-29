import { Routes, Route } from "react-router";
import Test from "./pages/Test.jsx";
import Home from "./pages/Home.jsx";
import "./App.css";

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/test" element={<Test />} />
      </Routes>
    </>
  );
}

export default App;
