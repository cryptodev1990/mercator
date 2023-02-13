import useSWR from "swr";
import qs from "qs";

const BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://dubo-api.mercator.tech/v1/dubo/query";

const fetcher = (url: string) => fetch(url).then((res) => res.json());

const getURL = ({
  databaseSchema,
  query,
}: {
  databaseSchema: DatabaseSchema;
  query: string;
}) =>
  query.length > 0
    ? `${BASE_URL}/${databaseSchema}?${qs.stringify({ user_query: query })}`
    : null;

const useDuboResults = ({
  query,
  databaseSchema,
}: {
  query: string;
  databaseSchema: DatabaseSchema;
}) => {
  const { data, error, isValidating, mutate, isLoading } = useSWR<any, Error>(
    getURL({ databaseSchema, query }),
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
