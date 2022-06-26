import React from "react";

import { Route } from "wouter";
import LandingPage from "./pages/landing";

function App() {
  React.useEffect(() => {
    // const url = String(process.env.REACT_APP_BACKEND_URL);
  }, []);
  return (
    <div>
      <Route path="/">
        <LandingPage />
      </Route>
    </div>
  );
}

export default App;
