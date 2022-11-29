import { useMatch } from "react-router";
import { Navbar } from "../../common/components/navbar";
import { AuthenticateAndCheckoutPage } from "./authenticate-and-checkout";

export const btnClasses = `
   transition duration-500 ease-in-out
   cursor-pointer
   font-semibold
   bg-slate-50 rounded border
   border-blue-500 p-3 sticky
   hover:bg-blue-500 hover:text-white
   bottom-0 left-0 mt-auto mb-0 text-center`;

export const ProductDisplayGroup = () => {
  return (
    <div className="flex sm:flex-row flex-col justify-center text-blue-100">
      <ProductDisplay enableCheckout>
        <h3 className="font-bold text-xl text-black select-none">
          Standard plan
        </h3>
        <p className="font-bold select-none">Two week free trial</p>
        <p>then $250/month</p>
        <br />
        <ul className="list-disc mx-3 select-none">
          <li>Upload or draw thousands of shapes</li>
          <li>Login with Google or Github</li>
          <li>Collaborate with others</li>
          <li>Share data from our Snowflake instance to yours directly</li>
        </ul>
        <br />
      </ProductDisplay>
      <ProductDisplay>
        <h3 className="font-bold text-xl text-black">Enterprise plan</h3>
        <p>Custom pricing</p>
        <br />
        <p className="select-none">
          Request custom features, receive 24/7 support in via a Slack shared
          channel private to your organization, and leverage our team's
          geospatial expertise.
        </p>
        <br />
        <button
          onClick={() => {
            // Open up an email and send it to us
            window.location.href = `mailto:support@mercator.tech
              ?subject=Enterprise%20Plan%20Request
              &body=Hi%20there%2C%0A%0AI%20would%20like%20to%20request%20an%20enterprise%20plan%20for%20my%20organization.%0A%0AThanks%2C%0A";`;
          }}
          className={btnClasses}
        >
          Contact us
        </button>
      </ProductDisplay>
    </div>
  );
};

const ProductDisplay = ({ children, enableCheckout }: any) => {
  // use react router to redirect to the checkout page
  return (
    <section className="text-blue-500 bg-slate-50 shadow-lg border border-blue-500 p-5 w-[350px] rounded-xl flex flex-col mx-2 my-4">
      {children}
      {enableCheckout && (
        <button
          className={btnClasses + " w-full"}
          id="checkout-and-portal-button"
          onClick={() => (window.location.href = "/subscribe/checkout")}
        >
          Subscribe
        </button>
      )}
    </section>
  );
};

const PricingCore = () => {
  return (
    <div>
      <div className="text-center">
        <h1 className="text-2xl text-slate-50">Pricing</h1>
        <p className="text-slate-50">
          Questions? Contact us at{" "}
          <a
            className="link link-primary text-slate-50"
            href="mailto:support@mercator.tech"
          >
            support@mercator.tech
          </a>
          .
        </p>
      </div>
      <div className="flex flex-row items-center justify-center my-auto">
        <ProductDisplayGroup />
      </div>
    </div>
  );
};

export default function SubscriptionPage() {
  const moveToCheckout = useMatch("/subscribe/checkout");

  return (
    <div className="section h-screen flex flex-col m-auto py-5 bg-blue-500">
      <Navbar />
      <div className="flex flex-col justify-center items-center p-10">
        {!moveToCheckout && <PricingCore />}
        {moveToCheckout && <AuthenticateAndCheckoutPage />}
      </div>
    </div>
  );
}
