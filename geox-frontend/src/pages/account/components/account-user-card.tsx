import { useAuth0, User } from "@auth0/auth0-react";
import { useApi } from "../../../hooks/use-api";
import { Card } from "./card";

function getOAuthProviderFromSub(sub: string | undefined): string {
  if (!sub) {
    return "";
  }
  if (sub.includes("google-oauth2")) {
    return "Google";
  } else if (sub.includes("facebook")) {
    return "Facebook";
  } else if (sub.includes("github")) {
    return "Github";
  } else if (sub.includes("twitter")) {
    return "Twitter";
  } else {
    return "Auth0";
  }
}

export const AccountUserCard = (): JSX.Element => {
  const { user, loginWithRedirect } = useAuth0<User>();
  const authProvider = getOAuthProviderFromSub(user?.sub);
  const isAuth0User = authProvider === "Auth0";
  // check if subscription is active
  const { status, loading } = useApi("/subscription_health");

  return (
    <Card title="Your profile">
      {[
        { key: "Name", value: user?.name },
        { key: "Email", value: user?.email },
        {
          key: "Verified Email",
          value: user?.email_verified ? "True" : "False",
        },
        { key: "OAuth Provider", value: authProvider },
        {
          key: "Subscription status",
          value: status === 200 ? "Valid" : "Inactive",
        },
      ].map((item) => {
        return (
          <div>
            <div className="font-semibold">{item.key}</div>
            <div>{item.value}</div>
          </div>
        );
      })}
      {isAuth0User && (
        <div>
          <p>
            Looking to reset your password? Go to{" "}
            <a
              className="link link-primary link-hover-primary"
              onClick={() => {
                loginWithRedirect({
                  returnTo: window.location.origin + "/dashboard",
                });
              }}
            >
              our sign in page.
            </a>
          </p>
        </div>
      )}
    </Card>
  );
};
