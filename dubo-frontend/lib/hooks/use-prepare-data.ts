import { useEffect, useState, useRef } from "react";
import { DataNames } from "../demo-data";

const usePrepareData = ({
  urlsOrFile,
  selectedData,
}: {
  selectedData: DataNames | null;
  urlsOrFile: (string | File)[];
}) => {
  const workerRef = useRef<Worker>();
  const [dfs, setDfs] = useState<DataFrame[] | undefined>(undefined);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    workerRef.current = new Worker(
      new URL("../workers/prepare-data-worker.ts", import.meta.url)
    );

    workerRef.current.onmessage = (
      event: MessageEvent<{ dfs?: DataFrame[]; error?: Error }>
    ) => {
      if (event.data.error) {
        setError(event.data.error.message);
      } else {
        setDfs(event.data.dfs);
        setError(null);
      }
    };

    return () => {
      workerRef?.current?.terminate();
    };
  }, []);

  useEffect(() => {
    workerRef?.current?.postMessage(urlsOrFile);
  }, [selectedData]);

  return {
    dfs,
    error,
    setDfs,
    setError,
  };
};

export default usePrepareData;
