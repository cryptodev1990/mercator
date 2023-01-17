import { useEffect, useState } from "react";
import initSqlJs, { Database } from "sql.js";
import { usePrepareData } from "./use-prepare-data";

export const useLocalSqlite = ({ urlsToData }: { urlsToData: string[] }) => {
  const [db, setDb] = useState<Database | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState<boolean>(false);

  useEffect(() => {
    initSqlJs({
      // Fetch sql.js wasm file from CDN
      // This way, we don't need to deal with webpack
      locateFile: (file) => `https://sql.js.org/dist/${file}`,
    })
      .then((SQL) => setDb(new SQL.Database()))
      .catch((err) => setError(err));

    return () => {
      if (db) {
        db.close();
        setDb(null);
      }
    };
  }, []);

  const {
    error: prepareError,
    preparing,
    prepared,
  } = usePrepareData({
    urlsToData,
    db,
  });

  const exec = (sql: string) => {
    try {
      if (!db) {
        throw new Error("db not initialized");
      }
      setRunning(true);
      const results = db.exec(sql);
      console.log(results);
      if (results.length === 0) {
        throw new Error("No results");
      }
      setRunning(false);
      return results;
    } catch (err: any) {
      setRunning(false);
      setError(err);
    }
  };

  if (running) {
    return { status: "running", error: prepareError, exec };
  }
  if (preparing) {
    return { status: "preparing", error: prepareError, exec };
  }
  if (prepared) {
    return { status: "ready", error: prepareError, exec };
  }

  return { exec, error };
};
