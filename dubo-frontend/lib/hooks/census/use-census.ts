import useSWR from "swr";
import qs from "qs";
import { readParquet } from "parquet-wasm";
import { tableFromIPC } from "@apache-arrow/es5-cjs/ipc/serialization";

import { base64ToString } from "../../utils";

const BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "https://dubo-api.mercator.tech";

const HEADER = "x-generated-sql";

const fetcher = async (url: string) =>
  new Promise(async (resolve, reject) => {
    try {
      const res = await fetch(url, {
        headers: {
          "Content-Type": "application/json",
          Accept: "binary/octet-stream",
        },
      });
      const base64EncodedSql = res.headers.get(HEADER);
      const ab = await res.arrayBuffer();
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
      // extract the generated SQL from the response headers
      const generatedSql = base64ToString(base64EncodedSql as string);
      resolve({
        records,
        generatedSql,
      });
    } catch (e) {
      reject(e);
    }
  });

const getURL = ({ query }: { query: string }) => {
  if (query.length === 0) return null;

  const queryParams = qs.stringify({ query });

  return `${BASE_URL}/demos/census?${queryParams}`;
};

const useCensus = ({ query }: { query: string }) => {
  const { data, error, isValidating, isLoading } = useSWR<any, Error>(
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

  const lookup = data?.records;
  const generatedSql = data?.generatedSql;

  return {
    data: {
      lookup,
      header: lookup ? Object.keys(lookup[Object.keys(lookup)[0]]) : [],
      generatedSql,
    },
    error,
    isValidating,
    isLoading,
  };
};

export default useCensus;
