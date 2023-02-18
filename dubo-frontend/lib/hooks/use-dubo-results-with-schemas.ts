import useSWR from "swr";
import { QueryExecResult } from "sql.js";

const BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "https://dubo-api.mercator.tech/v1/dubo/query";

const fetcher = ([query, schemas, dataSample]: [
  query: string,
  schemas?: QueryExecResult[],
  dataSample?: DataSample
]) => {
  const { data_header, data_sample } = dataSample || {};

  return fetch(BASE_URL, {
    method: "POST",
    headers: {
      accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      user_query: query,
      schemas: [schemas],
      data_header,
      data_sample,
    }),
  }).then((res) => res.json());
};

const useDuboResultsWithSchemas = ({
  query,
  schemas,
  dataSample,
}: {
  query: string;
  schemas?: QueryExecResult[];
  dataSample?: DataSample;
}) => {
  const { data, error, isValidating, mutate, isLoading } = useSWR<any, Error>(
    query.length > 0 ? [query, schemas, dataSample] : null,
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

export default useDuboResultsWithSchemas;
