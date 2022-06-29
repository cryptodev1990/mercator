import { useAuth0 } from "@auth0/auth0-react";
import { Navigate, useLocation } from "react-router";

const RequireAuth = () => {
  const { isAuthenticated } = useAuth0();
  const location = useLocation();
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
};

export default RequireAuth;
