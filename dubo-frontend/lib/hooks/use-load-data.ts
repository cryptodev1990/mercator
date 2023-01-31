import { sniff } from "../utils";

import { useEffect, useState } from "react";
import { Database } from "sql.js";

const useLoadData = ({
  dfs,
  db,
  setResults,
}: {
  dfs?: DataFrame[];
  db: Database | null;
  setResults: React.Dispatch<
    React.SetStateAction<initSqlJs.QueryExecResult[] | undefined>
  >;
}) => {
  const [error, setError] = useState<string | null>(null);
  const [schemas, setSchemas] = useState<
    initSqlJs.QueryExecResult[] | undefined
  >([]);
  const [loading, setLoading] = useState<boolean>(false);

  const fillDb = async ({ dfs }: { dfs?: DataFrame[] }) => {
    let dfNum = 0;
    if (db === null) {
      return;
    }

    if (!dfs) {
      return;
    }

    if (
      dfs.length === 1 &&
      (dfs[0].data.length === 0 || dfs[0].columns.length === 0)
    ) {
      setError("No data found, please check your file and try again");
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

    const schemas = db.exec(
      `SELECT sql FROM sqlite_schema WHERE name LIKE 'tbl_%'`
    );

    if (
      schemas?.length === 0 ||
      typeof schemas === "undefined" ||
      schemas[0].values.map((row: any) => row[0]).length === 0
    ) {
      setError("No tables found");
      return;
    } else {
      setSchemas(schemas[0].values.map((row: any) => row[0])[0]);

      const rows = db.exec("SELECT * FROM tbl_0 LIMIT 10");
      setResults(rows);
    }
  };

  useEffect(() => {
    if (!db) {
      return;
    }
    setLoading(true);
    fillDb({ dfs })
      .then(() => {
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [dfs, db]);

  return { error, setError, schemas, loading, setLoading };
};

export default useLoadData;