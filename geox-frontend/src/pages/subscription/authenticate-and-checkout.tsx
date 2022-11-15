import { useAuth0 } from "@auth0/auth0-react";
import { useEffect } from "react";
import { btnClasses } from ".";
import { useStripe } from "../../hooks/use-stripe";

const FRONTEND_CHECKOUT_URL =
  process.env.REACT_APP_FRONTEND_URL + "/subscribe/checkout";

export const AuthenticateAndCheckoutPage = () => {
  const { isAuthenticated, loginWithRedirect, isLoading } = useAuth0();
  const { createCheckoutSession } = useStripe();

  useEffect(() => {
    if (!isAuthenticated && !isLoading) {
      return;
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
