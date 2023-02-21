import { useEffect, useState, useRef } from "react";

const useSanitizeData = ({
  urlsOrFile,
}: {
  urlsOrFile: (string | File)[] | null;
}) => {
  const workerRef = useRef<Worker>();
  const [dfs, setDfs] = useState<DataFrame[] | undefined>(undefined);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    workerRef.current = new Worker(
      new URL("./sanitize-data-worker.ts", import.meta.url)
    );

    workerRef.current.onmessage = (
      event: MessageEvent<{ dfs?: DataFrame[]; error?: Error }>
    ) => {
      if (event.data.error) {
        setError(event.data.error.message);
        setDfs(undefined);
      } else {
        setDfs(event.data.dfs);
        setError(null);
      }
    };

    workerRef.current.onerror = (event: ErrorEvent) => {
      setError(event.message);
      setDfs(undefined);
    };

    return () => {
      workerRef?.current?.terminate();
    };
  }, []);

  useEffect(() => {
    setDfs(undefined);
    setError(null);
    workerRef?.current?.postMessage(urlsOrFile);
  }, [urlsOrFile]);

  return {
    dfs,
    error,
    setDfs,
    setError,
  };
};

export default useSanitizeData;
