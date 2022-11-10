import { BrowserRouter, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/landing";
import DashboardPage from "./pages/dashboard";
import RequireAuth from "./common/components/require-auth";
import { useAuth0 } from "@auth0/auth0-react";
import GeofencerPage from "./pages/geofencer";
import SubscriptionPage from "./pages/subscription";
import { useTokenInOpenApi } from "./hooks/use-token-in-openapi";
import AccountPage from "./pages/account";
import { Navbar } from "./common/components/navbar";
import { Link } from "react-router-dom";

// Create a 404 page
function NotFound() {
  return (
    <div
      className="
    h-screen w-screen
    bg-gradient-to-r from-blue-200 to-blue-700
    "
    >
      <div>
        <div className="max-w-5xl p-3 m-auto">
          <Navbar></Navbar>
        </div>
        <div className="flex flex-col mx-auto items-center py-[20vh] w-screen">
          <h2 className="text-white text-6xl font-bold">
            404 - Have no sphere
          </h2>
          <div className="text-white text-2xl pl-3 text-center">
            <p>
              We don't have a webpage at this URL.{" "}
              <Link className="link link-primary" to="/">
                Go back home.
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

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
        <Route
          path="/account/*"
          element={<RequireAuth page={<AccountPage />} />}
        />
        <Route path="/health" element={<HealthRedirect />} />
        <Route path="/login" element={<Login />} />
        <Route path="/privacy" element={<Privacy />} />
        <Route path="/terms" element={<Terms />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}

function App() {
  useTokenInOpenApi();

  return <RoutesIndex />;
}

export default App;
