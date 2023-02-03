import { readParquet } from "parquet-wasm";
import { tableFromIPC } from "@apache-arrow/es5-cjs/ipc/serialization";
import { useEffect, useState } from "react";

export const ZCTA_PARQUET_URL =
  "https://nkkohsotcmbtyzqpxukw.supabase.co/storage/v1/object/sign/queryable-data/zcta.parquet?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJxdWVyeWFibGUtZGF0YS96Y3RhLnBhcnF1ZXQiLCJpYXQiOjE2NzU0MDM1NzYsImV4cCI6MTcwNjkzOTU3Nn0.2hARprsxOaD1XeB1E83omKEugYmyjnIWBdXa-u22eX8&t=2023-02-03T05%3A52%3A56.768Z";

export const useZctaShapes = () => {
  const [zctaShapes, setZctaShapes] = useState<any[]>([]);
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    console.log("CALLED!");
    if (zctaShapes.length > 0) return;
    setIsLoading(true);
    fetch(ZCTA_PARQUET_URL, {
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
        const zctaCol = arrowTbl.getChild("zcta")?.toJSON();
        if (typeof zctaCol === "undefined" || zctaCol === null) {
          throw new Error("zcta column not found");
        }
        const geomColumn = arrowTbl?.getChild("geometry")?.toJSON();
        if (typeof geomColumn === "undefined" || geomColumn === null) {
          throw new Error("geometry column not found");
        }
        const output = [];
        for (let i = 0; i < arrowTbl.numRows; i++) {
          const zcta: string = zctaCol[i];
          const geom = JSON.parse(geomColumn[i]);
          if (geom.length !== 1) {
            for (const g of geom) {
              output.push({ zcta, geom: g });
            }
          } else {
            output.push({ zcta, geom });
          }
        }
        setZctaShapes(output);
        setIsLoading(false);
      })
      .catch((err) => {
        setError(err);
        setIsLoading(false);
      });
  }, []);
  return {
    zctaShapes,
    error,
    isLoading,
  };
};
