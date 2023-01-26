import { useEffect, useState } from "react";
import initSqlJs, { Database } from "sql.js";

const useDb = () => {
  const [db, setDb] = useState<Database | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<
    initSqlJs.QueryExecResult[] | undefined
  >([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    initSqlJs({
      // Fetch sql.js wasm file from CDN
      // This way, we don't need to deal with webpack
      locateFile: (file) => `https://sql.js.org/dist/${file}`,
    })
      .then((SQL) => {
        setLoading(false);
        setDb(new SQL.Database());
      })
      .catch((err) => {
        setLoading(false);
        setError(err);
      });

    return () => {
      if (db) {
        db.close();
        setDb(null);
      }
    };
  }, []);

  const exec = (sql: string) => {
    try {
      if (!db) {
        throw new Error("DB not initialized");
      }

      setResults(db.exec(sql));
    } catch (err: any) {
      setError(err);
    }
  };

  return {
    db,
    error,
    exec,
    loading,
    results,
    setResults,
  };
};

export default useDb;
