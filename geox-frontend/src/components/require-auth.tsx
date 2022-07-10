import { useAuth0 } from "@auth0/auth0-react";
import Loading from "react-loading";
import { Navigate, useLocation } from "react-router-dom";
import { isAdmin } from "../common";

function RequireAuth({
  page,
  adminOnly = false,
}: {
  page: JSX.Element;
  adminOnly?: boolean;
}) {
  let { isAuthenticated, user, isLoading } = useAuth0();
  let location = useLocation();

  if (isLoading) {
    return <Loading></Loading>;
  }

  const nav = <Navigate to="/login" state={{ from: location }} replace />;
  const userIsAdmin = user && !isLoading && isAdmin(user);

  if (adminOnly && !userIsAdmin) {
    return nav;
  }

  if (!isAuthenticated) {
    return nav;
  }

  return page;
}

export default RequireAuth;
