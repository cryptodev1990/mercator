import { useAuth0 } from "@auth0/auth0-react";
import { useEffect, useState } from "react";

export const useIdToken = () => {
  const { getAccessTokenSilently } = useAuth0();
  const [idToken, setIdToken] = useState<any>(null);

  useEffect(() => {
    getAccessTokenSilently({
      audience: process.env.REACT_APP_AUTH0_API_AUDIENCE,
      ignoreCache: false,
      detailedResponse: true,
    }).then((token) => {
      setIdToken(token.id_token);
    });
  }, []);

  return {
    idToken,
    setIdToken,
  };
};
