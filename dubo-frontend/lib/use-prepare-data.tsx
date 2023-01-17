import { JSONLoader, load, parse } from "@loaders.gl/core";
import { CSVLoader } from "@loaders.gl/csv";

import { useEffect, useState } from "react";
import { Database } from "sql.js";
import { DataFrame } from "./dubo-preview";
import { convertZip, sniff, sanitizeColumnNames } from "./dubo-client";

export const usePrepareData = ({
  urlsOrFile,
  db,
}: {
  urlsOrFile: (string | File)[];
  db: Database | null;
}) => {
  const [error, setError] = useState<string | null>(null);
  const [preparing, setPreparing] = useState<boolean>(false);
  const [prepared, setPrepared] = useState<boolean>(false);

  const loadData = async () => {
    setPreparing(true);
    const newDfs: DataFrame[] = [];
    for (const path of urlsOrFile) {
      const df: DataFrame = {
        columns: [],
        data: [],
      };
      if (typeof path === "string") {
        df.data = await load(path, [CSVLoader, JSONLoader]);
      } else if (path instanceof File) {
        df.data = await parse(path, [CSVLoader, JSONLoader]);
        console.table(df.data);
      } else {
        throw new Error("Unknown type");
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
      df.columns = Object.keys(df.data[0]) as string[];
      sanitizeColumnNames(df.columns);
      newDfs.push(df);
    }
    return newDfs;
  };

  const fillDb = async (dfs?: DataFrame[]) => {
    let dfNum = 0;
    if (db === null) {
      return;
    }
    if (!dfs) {
      return;
    }
    for (const df of dfs) {
      const types = sniff(df);
      const createTable = `DROP TABLE IF EXISTS tbl_${dfNum}; CREATE TABLE IF NOT EXISTS tbl_${dfNum} (${df.columns
        .map((col, i) => `${col} ${types[i]}`)
        .join(", ")});`;
      db.exec(createTable);
      for (const row of df.data) {
        const cols = df.columns.join(", ");
        // if the type is a string, we need to wrap it in quotes
        const insert = `INSERT INTO tbl_${dfNum}(${cols}) VALUES (${df.columns
          .map((col) => {
            const val = row[col];
            if (typeof val === "string") {
              return `'${val.replace(/'/g, "''")}'`;
            }
            if (typeof val === "number") {
              return val;
            }
            if (val === null) {
              return "NULL";
            }
            if (val === undefined) {
              return "NULL";
            }
            return val;
          })
          .join(", ")})`;
        db.run(insert);
      }
      dfNum += 1;
    }
    setPreparing(false);
    const rows = db.exec(`SELECT COUNT(*) FROM tbl_0 LIMIT 10`)[0].values[0][0];
    console.log(
      "Rows",
      // @ts-ignore
      rows
    );
    if (rows === 0) {
      setError("No data found, please check your file and try again");
    }
    console.log("done loading data");
  };

  useEffect(() => {
    if (!db) {
      return;
    }
    setPrepared(false);
    loadData()
      .then(fillDb)
      .then(() => {
        setPreparing(false);
        setPrepared(true);
      })
      .catch((err) => {
        setError(err);
        setPreparing(false);
        setPrepared(false);
      });
  }, [db, urlsOrFile]);

  return { error, preparing, prepared };
};
