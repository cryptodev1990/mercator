// Create a popup that tells the user they need to subscribe to use the geofence map

import { useApi } from "../../../hooks/use-api";
import { ProductDisplayGroup } from "../../../pages/subscription";

// Path: src/features/geofence-map/components/subscription-required-popup.tsx
// Compare this snippet from src/features/geofence-map/components/modals/index.tsx:

export const SubscriptionRequiredPopup = () => {
  const { status, loading } = useApi("/subscription_health");
  // link to the subscription page

  if (loading) {
    return <div>Loading...</div>;
  }
  if (status !== 402) {
    return null;
  }

  return (
    <div className="absolute top-0 left-0 w-full h-full flex justify-center items-center z-50">
      <div className="p-6 shadow z-10 rounded-xl bg-blue-400 text-white">
        <div className="text-center">
          <h1 className="text-5xl font-bold">Subscribe to Mercator</h1>
          <p>Activate your subscription to use Geofencer.</p>
          <div className="text-left">
            <ProductDisplayGroup />
          </div>
          <div className="text-left text-sm">
            Looking for something else? Go to the{" "}
            <a href="/dashboard" className="link link-primary">
              user dashboard
            </a>
          </div>
        </div>
      </div>
      <div className="absolute top-0 left-0 w-full h-full bg-blue-400 opacity-50"></div>
    </div>
  );
};
