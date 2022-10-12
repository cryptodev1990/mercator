import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import reportWebVitals from "./reportWebVitals";
import "./index.css";
import { Auth0Provider } from "@auth0/auth0-react";
import { QueryClient, QueryClientProvider } from "react-query";
import { startDatadogRUM } from "./lib/datadog-rum";

startDatadogRUM({
  /**
   * @TODO use a proper env config manager for frontend app
   */
  environment: process.env.VERCEL_ENV || "development",
  /**
   * @TODO use a proper env config manager for frontend app
   */
  gitSha: process.env.VERCEL_GIT_COMMIT_SHA || "local-development",
});

const container = document.getElementById("root")!;
const root = createRoot(container);

const queryClient = new QueryClient();

root.render(
  <>
    <Auth0Provider
      domain={process.env.REACT_APP_AUTH0_DOMAIN!}
      clientId={process.env.REACT_APP_AUTH0_CLIENT_ID!}
      useRefreshTokens={true}
      cacheLocation="localstorage"
      redirectUri={window.location.origin}
    >
      <QueryClientProvider client={queryClient}>
        <div className="h-full relative w-full bg-[#090A14] antialiased text-gray-600">
          <App />
        </div>
      </QueryClientProvider>
    </Auth0Provider>
  </>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
