import useSWR from "swr";
import qs from "qs";

import { base64ToString } from "../utils";

const BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://dubo-api.mercator.tech/v1/dubo/query";

const fetcher = async (url: string) => {
  const res = await fetch(url);
  const SQLHeader = res.headers.get("x-generated-sql");
  const convertedSQL = SQLHeader ? base64ToString(SQLHeader) : null;
  const body = await res.json();

  if (!res.ok && body?.detail) {
    return {
      query_text: convertedSQL,
      error: body.detail,
    };
  }

  return body;
};

const getURL = ({
  databaseSchema,
  query,
}: {
  databaseSchema: DatabaseSchema;
  query: string;
}) =>
  query.length > 0 && databaseSchema
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
