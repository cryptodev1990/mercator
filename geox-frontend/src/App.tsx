import React from "react";

import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useApi } from "./hooks/use-api";
import LandingPage from "./pages/landing";

function Logout() {
  window.location.replace(process.env.REACT_APP_FRONTEND_URL! + "/logout");
  return null;
}

function AuthRedirect() {
  window.location.replace(process.env.REACT_APP_FRONTEND_URL! + "/auth");
  return null;
}

function HealthRedirect() {
  window.location.replace(process.env.REACT_APP_FRONTEND_URL! + "/health");
  return null;
}

function RoutesIndex() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/logout" element={<Logout />} />
        <Route path="/auth" element={<AuthRedirect />} />
        <Route path="/health" element={<HealthRedirect />} />
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
