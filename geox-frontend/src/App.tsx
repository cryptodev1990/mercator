import { BrowserRouter, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/landing";
import DashboardPage from "./pages/dashboard";
import RequireAuth from "./common/components/require-auth";
import { useAuth0 } from "@auth0/auth0-react";
import GeofencerPage from "./pages/geofencer";
import SubscriptionPage from "./pages/subscription";
import { useTokenInOpenApi } from "./hooks/use-token-in-openapi";

function Logout() {
  const { logout } = useAuth0();
  logout({ returnTo: window.location.origin });
  return null;
}

function Login() {
  const { loginWithRedirect } = useAuth0();
  loginWithRedirect({ returnTo: window.location.origin + "/dashboard" });
  return null;
}

function HealthRedirect() {
  // Pass through to proxy server
  // See setupProxy.js
  window.location.replace(process.env.REACT_APP_FRONTEND_URL! + "/health");
  return null;
}

function Terms(): null {
  const url =
    "https://docs.google.com/document/d/e/2PACX-1vSMcKSpjwh7Vhj0xNC38lmoRwkAdpMlGXYl5uOWUcID-PhtzTp06FPCWuvqJJUtlfPkVaYJ6_R1lswK/pub";
  window.location.replace(url);
  return null;
}

function Privacy(): null {
  const url =
    "https://docs.google.com/document/d/e/2PACX-1vS5rxku7DRfwI9wjoJ6wSyir8Jy3IAJGaGABTf54DO_v_JiZjACAr0DsOzbp6xiduQbV0YI2mJeLHL6/pub";
  window.location.replace(url);
  return null;
}

function RoutesIndex() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />

        <Route
          path="/dashboard"
          element={<RequireAuth page={<DashboardPage />} />}
        />
        <Route path="/subscribe" element={<SubscriptionPage />}>
          <Route path="checkout" element={<SubscriptionPage />} />
        </Route>
        <Route
          path="/subscribe"
          element={<RequireAuth page={<SubscriptionPage />} />}
        />
        <Route
          path="/geofencer"
          element={<RequireAuth page={<GeofencerPage />} />}
        />
        <Route path="/logout" element={<RequireAuth page={<Logout />} />} />
        <Route path="/health" element={<HealthRedirect />} />
        <Route path="/login" element={<Login />} />
        <Route path="/privacy" element={<Privacy />} />
        <Route path="/terms" element={<Terms />} />
      </Routes>
    </BrowserRouter>
  );
}

function App() {
  useTokenInOpenApi();

  return <RoutesIndex />;
}

export default App;
