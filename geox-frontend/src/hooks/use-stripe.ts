import { useAuth0 } from "@auth0/auth0-react";
import { toast } from "react-hot-toast";

const STRIPE_CHECKOUT_URL =
  process.env.REACT_APP_BACKEND_URL + "/billing/create-checkout-session";
const STRIPE_CUSTOMER_URL =
  process.env.REACT_APP_BACKEND_URL + "/billing/create-customer-portal-session";

export const useStripe = () => {
  const { getAccessTokenSilently } = useAuth0();
  async function accessToken() {
    return await getAccessTokenSilently({
      audience: process.env.REACT_APP_AUTH0_API_AUDIENCE,
      ignoreCache: false,
      detailedResponse: true,
    });
  }

  async function createCheckoutSession() {
    const { id_token } = await accessToken();
    const response = await window.fetch(STRIPE_CHECKOUT_URL, {
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

  async function createPaymentSession() {
    const { id_token } = await accessToken();
    const response = await window.fetch(STRIPE_CUSTOMER_URL, {
      headers: {
        Authorization: `Bearer ${id_token}`,
        "Content-Type": "application/json",
      },
      method: "POST",
      body: JSON.stringify({
        return_url: process.env.REACT_APP_FRONTEND_URL + "/account",
      }),
    });
    const data = await response.json();
    if (response.status !== 200) {
      return {
        errorDetail: data,
      };
    }
    window.location.href = data.url;
  }

  return {
    createCheckoutSession,
    createPaymentSession,
  };
};
