import useSWR from "swr";
import { getURLWithQueryParams, jsonFetcher } from "../hook-utils";

const URL_PATH = "/demos/census/autocomplete";

const useCensusAutocomplete = ({ text }: { text: string }) => {
  const {
    data: suggestions,
    error,
    isValidating,
    isLoading,
  } = useSWR<any, Error>(
    getURLWithQueryParams({ urlPath: URL_PATH, query: { text } }),
    jsonFetcher,
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
