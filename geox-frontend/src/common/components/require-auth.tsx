import { useAuth0 } from "@auth0/auth0-react";
import { useEffect, useState } from "react";
import Loading from "react-loading";
import { Navigate, useLocation } from "react-router-dom";
import { isAdmin } from "../../common";
import { useTokenInOpenApi } from "../../hooks/use-token-in-openapi";

function RequireAuth({
  page,
  adminOnly = false,
}: {
  page: JSX.Element;
  adminOnly?: boolean;
}) {
  let { isAuthenticated, user, isLoading: authLoading } = useAuth0();
  const { isTokenSet } = useTokenInOpenApi();
  let location = useLocation();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isAuthenticated && isTokenSet) {
      setLoading(false);
    }
  }, [authLoading, isTokenSet, isAuthenticated]);

  useEffect(() => {
    setTimeout(() => {
      setLoading(false);
    }, 2000);
  }, []);

  if (loading) {
    return (
      <div className="fixed bg-slate-600 h-screen w-screen">
        <Loading delay={500}></Loading>
      </div>
    );
  }

  const nav = <Navigate to="/login" state={{ from: location }} replace />;
  const userIsAdmin = user && !authLoading && isAdmin(user);

  if (adminOnly && !userIsAdmin) {
    return nav;
  }

  if (!isAuthenticated) {
    return nav;
  }

  return page;
}

export default RequireAuth;
