import useSWR from "swr";
import qs from "qs";
import { readParquet } from "parquet-wasm";
import { tableFromIPC } from "@apache-arrow/es5-cjs/ipc/serialization";

const BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "https://dubo-api.mercator.tech";

const fetcher = (url: string) =>
  fetch(url, {
    headers: {
      "Content-Type": "application/json",
      Accept: "binary/octet-stream",
    },
  })
    .then((res) => res.arrayBuffer())
    .then((ab) => {
      const uint8 = new Uint8Array(ab);
      const arrowTbl = tableFromIPC(readParquet(uint8));
      if (typeof arrowTbl === "undefined" || arrowTbl === null) {
        throw new Error("arrow table not found");
      }
      const zctaList = arrowTbl.getChild("zcta")?.toJSON();
      if (typeof zctaList === "undefined" || zctaList === null) {
        throw new Error("zcta column not found");
      }
      const records: {
        [key: string]: any;
      } = {};
      for (let i = 0; i < arrowTbl.numRows; i++) {
        const zcta: string = zctaList[i];
        records[zcta] = {};
        for (let j = 0; j < arrowTbl.schema.fields.length; j++) {
          const field = arrowTbl.schema.fields[j];
          if (field.name === "zcta") continue;
          // @ts-ignore
          records[zcta][field.name] = arrowTbl?.getChild(field.name).get(i);
        }
      }
      return records;
    });

const getURL = ({ query }: { query: string }) => {
  if (query.length === 0) return null;

  const queryParams = qs.stringify({ query });

  return `${BASE_URL}/demos/census?${queryParams}`;
};

const useCensus = ({ query }: { query: string }) => {
  const {
    data: lookup,
    error,
    isValidating,
    isLoading,
  } = useSWR<any, Error>(
    getURL({
      query,
    }),
    fetcher,
    {
      shouldRetryOnError: false,
      isPaused: () => query === undefined,
      revalidateIfStale: false,
      revalidateOnReconnect: false,
      revalidateOnFocus: false,
    }
  );

  return {
    data: {
      lookup,
      header: lookup ? Object.keys(lookup[Object.keys(lookup)[0]]) : [],
    },
    error,
    isValidating,
    isLoading,
  };
};

export default useCensus;
