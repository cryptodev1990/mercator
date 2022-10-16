import React from "react";
import { useAuth0 } from "@auth0/auth0-react";

/**
 * Handle identifying logged in users with Intercom.
 */
export function useIntercom(): void {
  const { user } = useAuth0();

  React.useEffect(() => {
    if (user) {
      // @ts-ignore
      window.Intercom("boot", {
        app_id: process.env.REACT_APP_INTERCOM_APP_ID,
        email: user.email,
      });
    }
  }, [user]);
}
