import React from "react";

import { BrowserRouter, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/landing";
import DashboardPage from "./pages/dashboard";
import RequireAuth from "./components/require-auth";
import { useAuth0 } from "@auth0/auth0-react";

function Logout() {
  const { logout } = useAuth0();
  logout({ returnTo: window.location.origin });
  return null;
}

function Login() {
  const { loginWithRedirect } = useAuth0();
  loginWithRedirect({ returnTo: window.location.origin });
  return null;
}

function HealthRedirect() {
  // Pass through to proxy server
  // See setupProxy.js
  window.location.replace(process.env.REACT_APP_FRONTEND_URL! + "/health");
  return null;
}

function RoutesIndex() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />

        <Route
          path="/dashboard"
          element={
            <RequireAuth>
              <DashboardPage />
            </RequireAuth>
          }
        />
        <Route
          path="/logout"
          element={
            <RequireAuth>
              <Logout />
            </RequireAuth>
          }
        />
        <Route path="/health" element={<HealthRedirect />} />
        <Route path="/login" element={<Login />} />
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
