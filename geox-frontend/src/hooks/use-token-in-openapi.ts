import { useAuth0 } from "@auth0/auth0-react";
import { useEffect, useState } from "react";
import { OpenAPI } from "../client";

export function useTokenInOpenApi() {
  const { isAuthenticated } = useAuth0();
  const { getAccessTokenSilently } = useAuth0();
  const [isTokenSet, setIsTokenSet] = useState(false);
  useEffect(() => {
    if (isAuthenticated) {
      getAccessTokenSilently({
        audience: process.env.REACT_APP_AUTH0_API_AUDIENCE,
        ignoreCache: false,
        detailedResponse: true,
      }).then((res) => {
        OpenAPI.TOKEN = res.id_token;
        setIsTokenSet(true);
      });
    }
  }, [isAuthenticated, getAccessTokenSilently]);
  return { isTokenSet };
}
