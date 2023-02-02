import useSWR from "swr";
import qs from "qs";
import { QueryExecResult } from "sql.js";

const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "https://dubo-api.mercator.tech/v1/dubo/query";

const fetcher = (url: string) => fetch(url).then((res) => res.json());

const getURL = ({
  query,
  schemas,
  databaseSchema,
}: {
  query: string;
  schemas?: QueryExecResult[];
  databaseSchema?: DatabaseSchema;
}) => {
  if (!(query.length > 0) || (!schemas && !databaseSchema)) return null;

  const queryParams = qs.stringify({ schemas, user_query: query });

  if (databaseSchema) return `${BASE_URL}/${databaseSchema}?${queryParams}`;

  return `${BASE_URL}?${queryParams}`;
};

const useDuboResults = ({
  query,
  schemas,
  databaseSchema,
}: {
  query: string;
  schemas?: QueryExecResult[];
  databaseSchema?: DatabaseSchema;
}) => {
  const { data, error, isValidating, mutate, isLoading } = useSWR<any, Error>(
    getURL({ query, schemas, databaseSchema }),
    fetcher,
    {
      shouldRetryOnError: false,
      revalidateIfStale: false,
      revalidateOnReconnect: false,
      revalidateOnFocus: false,
    }
  );

  return {
    data,
    error,
    isValidating,
    mutate,
    isLoading,
  };
};

export default useDuboResults;
