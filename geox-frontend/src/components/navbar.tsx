import { useAuth0 } from "@auth0/auth0-react";
import smallLogo from "../common/assets/small-logo.svg";
import logo from "../common/assets/mercator-logo.svg";
import ReactLoading from "react-loading";
import { useApi } from "../hooks/use-api";
import { useNavigate, useMatch } from "react-router-dom";

const Navbar: React.FC = () => {
  const {
    loginWithRedirect,
    isAuthenticated,
    isLoading,
    // getAccessTokenSilently,
  } = useAuth0();
  let navigate = useNavigate();
  const onDashboard = useMatch("/dashboard/*");

  useApi("/protected_health");

  let loginText = "";
  if (!isLoading) {
    loginText = isAuthenticated
      ? onDashboard
        ? "Profile"
        : "Dashboard"
      : "Login";
  }

  const css =
    "relative max-w-5xl z-10 container mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between font-semibold text-sm text-white";
  return (
    <header className={css}>
      <nav aria-label="Logo menu" className="relative z-50 flex">
        <a href="/">
          <img
            src={isAuthenticated && onDashboard ? smallLogo : logo}
            alt="logo"
            className="h-10"
          />
        </a>
      </nav>
      <nav aria-label="Main menu" className="flex">
        <button
          disabled={isLoading}
          onClick={
            isAuthenticated
              ? () => navigate("/dashboard")
              : () => loginWithRedirect()
          }
          className="text-base sm:text-sm px-6 button lg:button-sm bg-ublue hover:bg-violet-600 text-white font-bold transition-all p-2 rounded"
        >
          {isLoading && (
            <ReactLoading type={"spin"} height={"1rem"} width={"1rem"} />
          )}
          {loginText}
        </button>
      </nav>
    </header>
  );
};

export { Navbar };
