import { toast, Toaster } from "react-hot-toast";
import { useStripe } from "../../../hooks/use-stripe";
import { Card } from "./card";

const AccountBillingCard = (): JSX.Element => {
  const { createPaymentSession } = useStripe();

  return (
    <Card title="Billing">
      <Toaster />
      <p>
        <span
          onClick={async () => {
            const res = await createPaymentSession();
            if (res !== undefined) {
              toast.error(res?.errorDetail?.detail ?? "Unknown error");
            }
          }}
          className="link link-primary"
        >
          Click here
        </span>{" "}
        to update your payment profile, cancel your subscription, or download
        invoices.
      </p>
      <p>Questions? Contact support@mercator.tech.</p>
    </Card>
  );
};

export default AccountBillingCard;
