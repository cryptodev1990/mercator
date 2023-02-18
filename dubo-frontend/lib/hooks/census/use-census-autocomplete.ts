import useSWR from "swr";
import qs from "qs";

const BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "https://dubo-api.mercator.tech";
const URL_PATH = "/demos/census/autocomplete";

const getURLWithQueryParams = ({
  urlPath,
  query,
}: {
  urlPath: string;
  query: Record<string, string | number | boolean>;
}) => {
  if (query.length === 0) return null;

  if (urlPath[0] !== "/") {
    urlPath = `/${urlPath}`;
  }

  const queryParams = qs.stringify(query);

  return `${BASE_URL}${urlPath}?${queryParams}`;
};

const fetcher = (url: string) =>
  fetch(url, {
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
  })
    .then((res) => res.json())
    .catch((err) => {
      console.error(err);
      throw err;
    });

const useCensusAutocomplete = ({ text }: { text: string }) => {
  const {
    data: suggestions,
    error,
    isValidating,
    isLoading,
  } = useSWR<any, Error>(
    getURLWithQueryParams({ urlPath: URL_PATH, query: { text } }),
    fetcher,
    {
      // keep data while loading
      revalidateOnFocus: false,
      keepPreviousData: true,
    }
  );

  return {
    data: {
      suggestions,
    },
    error,
    isValidating,
    isLoading,
  };
};

export default useCensusAutocomplete;
