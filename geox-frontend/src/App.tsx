import React from "react";

import { BrowserRouter, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/landing";

function Logout() {
  window.location.replace(process.env.REACT_FRONTEND_URL! + "/logout");
  return null;
}

function RoutesIndex() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/logout" element={<Logout />} />
      </Routes>
    </BrowserRouter>
  );
}

function App() {
  React.useEffect(() => {
    // const url = String(process.env.REACT_APP_BACKEND_URL);
  }, []);
  return <RoutesIndex />;
}

export default App;
