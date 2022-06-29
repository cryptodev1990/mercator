import { useAuth0 } from "@auth0/auth0-react";
import logo from "./mercator-logo.svg";
import ReactLoading from "react-loading";
// import { useApi } from "../hooks/use-api";

const Navbar: React.FC = () => {
  const {
    loginWithRedirect,
    isAuthenticated,
    isLoading,
    logout,
    // getAccessTokenSilently,
  } = useAuth0();

  // const [authToken, setAuthToken] = useState<string>("");

  // useEffect(() => {
  //   async function getToken() {
  //     const token = await getAccessTokenSilently({
  //       ignoreCache: true,
  //       audience: process.env.REACT_APP_AUTH0_API_AUDIENCE,
  //       detailedResponse: true,
  //     });
  //     setAuthToken(token.access_token);
  //   }
  // }, [getAccessTokenSilently, isAuthenticated]);

  // useApi("http://localhost:8080/verify_jwt");

  const css =
    "relative max-w-5xl bg-red z-10 container mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-24 font-semibold text-sm text-white";
  return (
    <header className={css}>
      <nav aria-label="Logo menu" className="relative z-50 flex">
        <a href="/">
          <img src={logo} alt="logo" className="h-10" />
        </a>
      </nav>
      <nav aria-label="Main menu" className="flex">
        <button
          disabled={isLoading}
          onClick={
            isAuthenticated
              ? () => logout({ returnTo: window.location.origin })
              : () => loginWithRedirect()
          }
          className="text-base sm:text-sm px-6 button lg:button-sm bg-ublue hover:bg-violet-600 text-white font-bold transition-all p-2 rounded"
        >
          {isLoading && (
            <ReactLoading type={"spin"} height={"1rem"} width={"1rem"} />
          )}
          {!isLoading && isAuthenticated ? "Log Out" : "Login"}
        </button>
      </nav>
    </header>
  );
};

export { Navbar };
