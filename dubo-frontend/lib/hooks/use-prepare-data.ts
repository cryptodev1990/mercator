import { convertZip, sanitizeColumnNames } from "../utils";
import { JSONLoader, load } from "@loaders.gl/core";
import { CSVLoader } from "@loaders.gl/csv";
import { useEffect, useState } from "react";
import { DataNames } from "../demo-data";

const usePrepareData = ({
  urlsOrFile,
  selectedData,
}: {
  selectedData: DataNames | null;
  urlsOrFile: (string | File)[];
}) => {
  const [dfs, setDfs] = useState<DataFrame[] | undefined>(undefined);
  const [error, setError] = useState<string | null>(null);

  const sanitize = async () => {
    const newDfs: DataFrame[] = [];
    for (const path of urlsOrFile) {
      const df: DataFrame = {
        columns: [],
        data: [],
      };

      try {
        if (typeof path === "string" || path instanceof File) {
          df.data = await load(path, [CSVLoader, JSONLoader]);
          setError(null);
        } else {
          setError("Unknown type");
        }
      } catch (err: any) {
        setError(err.message);
      }

      // apply the function to convert any of the data frame records to a string if ZIP is a number
      df.data = df.data.map((row: any) => {
        for (const key of Object.keys(row)) {
          if (
            ["zcta", "zip", "zip_code"].includes(key) &&
            typeof row[key] === "number"
          ) {
            row[key] = convertZip(row[key]);
          }
        }
        return row;
      });

      // We assume the header is properly set in the first row
      df.columns = df.data[0] ? (Object.keys(df.data[0]) as string[]) : [];
      sanitizeColumnNames(df.columns);
      newDfs.push(df);
    }

    return newDfs;
  };

  useEffect(() => {
    sanitize()
      .then((dfs) => setDfs(dfs))
      .catch((err) => setError(err.message));
  }, [selectedData]);

  return {
    dfs,
    error,
    setDfs,
    setError,
  };
};

export default usePrepareData;
