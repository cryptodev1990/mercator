import { useAuth0 } from "@auth0/auth0-react";
import { useEffect } from "react";
import { btnClasses } from ".";

const FRONTEND_CHECKOUT_URL =
  process.env.REACT_APP_FRONTEND_URL + "/subscribe/checkout";
const BACKEND_STRIPE_URL =
  process.env.REACT_APP_BACKEND_URL + "/billing/create-checkout-session";

export const AuthenticateAndCheckoutPage = () => {
  const { isAuthenticated, loginWithRedirect, isLoading } = useAuth0();
  const { getAccessTokenSilently } = useAuth0();

  useEffect(() => {
    if (!isAuthenticated && !isLoading) {
      return;
    }
    async function accessToken() {
      return await getAccessTokenSilently({
        audience: process.env.REACT_APP_AUTH0_API_AUDIENCE,
        ignoreCache: false,
        detailedResponse: true,
      });
    }
    async function createCheckoutSession() {
      const { id_token } = await accessToken();
      const response = await window.fetch(BACKEND_STRIPE_URL, {
        headers: {
          Authorization: `Bearer ${id_token}`,
          "Content-Type": "application/json",
        },
        method: "POST",
        body: JSON.stringify({
          price_id: process.env.REACT_APP_STRIPE_PRICE_ID,
          success_url: process.env.REACT_APP_FRONTEND_URL + "/dashboard",
          cancel_url: process.env.REACT_APP_FRONTEND_URL + "/subscribe",
        }),
      });
      window.location.href = await response.json().then((data) => data.url);
    }
    createCheckoutSession();
  }, [isAuthenticated]);

  if (isLoading) {
    return <div className="text-2xl text-white">Verifying auth...</div>;
  }

  if (isAuthenticated) {
    return <div className="text-2xl text-white">Redirecting to Stripe...</div>;
  }

  return (
    <div className="text-2xl text-white">
      <div>
        {/* Header describing the product */}
        <h1 className="text-3xl text-slate-50">Create an account</h1>
        <p className="text-lg text-slate-50">
          You need an account to activate your free trial. Already have an
          account?{" "}
          <a
            className="link link-primary text-slate-50"
            onClick={() =>
              loginWithRedirect({
                redirectUri: FRONTEND_CHECKOUT_URL,
              })
            }
          >
            Log in
          </a>
          .
        </p>
        <br />
      </div>
      <button
        className={btnClasses + " text-blue-500"}
        onClick={() =>
          loginWithRedirect({
            redirectUri: FRONTEND_CHECKOUT_URL,
            screen_hint: "signup",
          })
        }
      >
        Sign up
      </button>
    </div>
  );
};
