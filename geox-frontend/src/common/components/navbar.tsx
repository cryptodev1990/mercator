import { useAuth0 } from "@auth0/auth0-react";
import smallLogo from "../assets/small-logo.svg";
import logo from "../assets/mercator-logo.svg";
import ReactLoading from "react-loading";
import { useNavigate, useMatch } from "react-router-dom";
import Dropdown from "./dropdown";
import { FlashButton } from "./button";
import clsx from "clsx";

const LoginButton = () => {
  const navigate = useNavigate();
  const { isLoading, isAuthenticated, loginWithRedirect } = useAuth0();
  return (
    <FlashButton
      id="login"
      disabled={isLoading}
      onClick={
        isAuthenticated
          ? () => navigate("/dashboard")
          : () =>
              loginWithRedirect({
                returnTo: window.location.origin + "/dashboard",
              })
      }
    >
      {isLoading ? (
        <ReactLoading type={"spin"} height={"1rem"} width={"1rem"} />
      ) : (
        "Login"
      )}
    </FlashButton>
  );
};

const Navbar: React.FC = () => {
  const { isAuthenticated } = useAuth0();
  const onDashboard = useMatch("/dashboard/*");
  const onHomepage = useMatch("/");
  const navigate = useNavigate();

  let cornerButton = null;
  if (!isAuthenticated) {
    cornerButton = <LoginButton />;
  } else if (onHomepage) {
    cornerButton = (
      <FlashButton onClick={() => navigate("/dashboard")}>
        Dashboard
      </FlashButton>
    );
  } else {
    cornerButton = <Dropdown />;
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
            className={clsx("h-10", onHomepage && !isAuthenticated && "hidden")}
          />
        </a>
        <div className="space-x-10">
          {onHomepage && (
            <div>
              <a className="hover:underline" href="/subscribe">
                Pricing
              </a>
            </div>
          )}
        </div>
      </nav>
      <nav aria-label="Main menu" className="flex">
        {cornerButton}
      </nav>
    </header>
  );
};

export { Navbar };
