import { useEffect, useState, useRef, useCallback } from "react";
import { QueryExecResult, SqlValue } from "sql.js";

import { sniff } from "../utils";

const useLoadData = ({ dfs }: { dfs?: DataFrame[] }) => {
  const workerRef = useRef<Worker>();
  const [error, setError] = useState<string | null>(null);
  const [schemas, setSchemas] = useState<QueryExecResult[] | undefined>([]);
  const [tables, setTables] = useState<SqlValue[] | undefined>([]);
  const [sample, setSample] = useState<DataSample | undefined>(undefined);
  const [loading, setLoading] = useState<boolean>(true);
  const [results, setResults] = useState<QueryExecResult[] | undefined>([]);
  const [resultsLoading, setResultsLoading] = useState<boolean>(false);
  const [resultsError, setResultsError] = useState<string | null>(null);

  useEffect(() => {
    workerRef.current = new Worker(
      new URL(
        "../../node_modules/sql.js/dist/worker.sql-wasm.js",
        import.meta.url
      ),
      { type: "module" }
    );

    workerRef.current.onmessage = (
      event: MessageEvent<{
        id: string;
        results: QueryExecResult[];
        error?: string;
      }>
    ) => {
      if (event.data.error) {
        setResults(undefined);
        setResultsError(event.data.error);
        setResultsLoading(false);
      }

      if (event.data.id === "create-table") {
        workerRef?.current?.postMessage({
          id: "schema",
          action: "exec",
          sql: `SELECT sql FROM sqlite_schema WHERE name LIKE 'tbl_%'`,
        });
      }

      if (event.data.id === "schema") {
        const schemas = event.data.results;
        if (
          schemas?.length === 0 ||
          schemas === undefined ||
          schemas[0].values.map((row: any) => row[0]).length === 0
        ) {
          setError("No tables found");
        } else {
          setSchemas(schemas[0].values.map((row: any) => row[0])[0]);
        }

        workerRef?.current?.postMessage({
          id: "tables",
          action: "exec",
          sql: "SELECT name FROM sqlite_schema WHERE type ='table' AND name NOT LIKE 'sqlite_%';",
        });
      }

      if (event.data.id === "tables") {
        setTables(event.data.results[0].values.map((v) => v[0]));
      }

      if (event.data.id === "insert-rows") {
        workerRef?.current?.postMessage({
          id: "sample",
          action: "exec",
          sql: "SELECT * FROM tbl_0 LIMIT 10",
        });
      }

      if (event.data.id === "sample") {
        const rows = event.data.results;
        setResults(rows);
        setSample({
          data_header: rows[0].columns,
          data_sample: rows[0].values.slice(0, 5),
        });
        setLoading(false);
      }

      if (event.data.id === "exec") {
        const rows = event.data.results;
        setResults(rows);
        setResultsLoading(false);
      }
    };

    workerRef.current.onerror = (event: ErrorEvent) => {
      setError(event.message);
      setLoading(false);
    };

    return () => {
      workerRef?.current?.terminate();
    };
  }, []);

  const loadData = async ({ dfs }: { dfs?: DataFrame[] }) => {
    if (workerRef?.current === null || !dfs) {
      return;
    }
    tables?.forEach((table) => {
      workerRef?.current?.postMessage({
        id: "drop-table",
        action: "exec",
        sql: `DROP TABLE IF EXISTS ${table};`,
      });
    });

    setTables(undefined);

    dfs.forEach((df, index) => {
      const types = sniff(df);
      const createTable = `CREATE TABLE IF NOT EXISTS tbl_${index} (${df.columns
        .map((col, i) => `${col} ${types[i]}`)
        .join(", ")});`;

      workerRef?.current?.postMessage({
        id: "create-table",
        action: "exec",
        sql: createTable,
      });
    });

    dfs.forEach((df, index) => {
      const cols = df.columns.join(", ");
      const insertRows = df.data.reduce(
        (acc, row, index) =>
          `${acc}(${df.columns
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
            .join(", ")})${index === df.data.length - 1 ? ";" : ","}\n`,
        `INSERT INTO tbl_${index}(${cols}) VALUES\n`
      );

      workerRef?.current?.postMessage({
        id: "insert-rows",
        action: "exec",
        sql: insertRows,
      });
    });
  };

  useEffect(() => {
    loadData({ dfs });
  }, [dfs]);

  const exec = useCallback(
    (sql: string) => {
      setResults(undefined);
      setResultsError(null);
      setResultsLoading(true);
      workerRef?.current?.postMessage({ id: "exec", action: "exec", sql });
    },
    [setResults, setResultsError, setResultsLoading, workerRef?.current]
  );

  return {
    exec,
    error,
    setError,
    schemas,
    loading,
    setLoading,
    sample,
    results,
    setResults,
    resultsLoading,
    resultsError,
    setResultsError,
  };
};

export default useLoadData;
