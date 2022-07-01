import { useAuth0 } from "@auth0/auth0-react";
import Loading from "react-loading";
import { Navigate, useLocation } from "react-router-dom";

function RequireAuth({ children }: { children: JSX.Element }) {
  let { isAuthenticated, isLoading } = useAuth0();
  let location = useLocation();

  if (isLoading) {
    return <Loading></Loading>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}

export default RequireAuth;
