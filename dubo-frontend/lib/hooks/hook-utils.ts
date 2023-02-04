import qs from "qs";

const BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "https://dubo-api.mercator.tech";

export const getURLWithQueryParams = ({
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

export const jsonFetcher = (url: string) =>
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
