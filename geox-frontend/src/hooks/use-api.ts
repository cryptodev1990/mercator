import { useEffect, useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";

interface UseApiOptions {
  headers?: HeadersInit;
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
  const [refreshIndex, setRefreshIndex] = useState(0);

  useEffect(() => {
    (async () => {
      try {
        const accessToken = await getAccessTokenSilently({
          audience: process.env.REACT_APP_AUTH0_API_AUDIENCE,
        });
        const headers = {
          ...fetchOptions.headers,
          // Add the Authorization header to the existing headers
          Authorization: `Bearer ${accessToken}`,
        };

        const res = await window.fetch(url, {
          ...fetchOptions,
          headers,
        });
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
  }, [refreshIndex]);

  return {
    ...state,
    refresh: () => setRefreshIndex(refreshIndex + 1),
  };
};
