import { useEffect, useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";

interface UseApiOptions {
  headers?: HeadersInit;
  method?: string;
}

type ErrorWithMessage = {
  message: string;
};

type Nullable<T> = T | null;

interface ApiState {
  error: Nullable<ErrorWithMessage>;
  data: Nullable<Array<any>>;
  loading: boolean;
}

// https://github.com/auth0/auth0-react/blob/master/EXAMPLES.md#4-create-a-useapi-hook-for-accessing-protected-apis-with-an-access-token
export const useApi = (url: string, fetchOptions: UseApiOptions = {}) => {
  const { getAccessTokenSilently } = useAuth0();
  const [state, setState] = useState<ApiState>({
    error: null,
    loading: true,
    data: null,
  });

  useEffect(() => {
    (async () => {
      try {
        const token = await getAccessTokenSilently({
          audience: process.env.REACT_APP_AUTH0_API_AUDIENCE,
          ignoreCache: false,
          detailedResponse: true,
        });
        const headers = {
          ...fetchOptions.headers,
          // Add the Authorization header to the existing headers
          Authorization: `Bearer ${token.id_token}`,
        };

        const res = await window.fetch(
          process.env.REACT_APP_BACKEND_URL + url,
          {
            ...fetchOptions,
            headers,
          }
        );
        setState({
          ...state,
          data: await res.json(),
          error: null,
          loading: false,
        });
      } catch (error) {
        let message = "unknown error";
        if (error instanceof Error) message = error.message;
        setState({
          ...state,
          error: { message },
          loading: false,
        });
      }
    })();
  }, [url]);

  return {
    ...state,
  };
};
