import { useEffect, useState } from "react";
import duboQuery from "../lib/dubo-client";
import DataFrameViewer from "./data-frame-viewer";
import { FaPlay, FaSpinner } from "react-icons/fa";
import simplur from "simplur";

const Demos = ({ databaseSchema }: { databaseSchema: DatabaseSchema }) => {
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState<string>(
    "Show ten rows of data from the transactions table"
  );
  const [duboResponse, setDuboResponse] = useState<any>(null);
  const [awaitingResult, setAwaitingResult] = useState<boolean>(false);

  const handleQuery = async (sql: string) => {
    setAwaitingResult(true);
    setDuboResponse(null);
    setError(null);
    const duboRes = await duboQuery(sql, undefined, databaseSchema);

    if (duboRes) {
      setDuboResponse(duboRes);
      setAwaitingResult(false);
    } else {
      setError("Query failed. Try a different query.");
      setAwaitingResult(false);
    }
  };

  useEffect(() => {
    if (databaseSchema) {
      handleQuery(query);
    }
  }, [databaseSchema]);

  const header = duboResponse
    ? Object.keys(duboResponse?.results[0]).filter(
        (c) => c !== "inputs" && c !== "outputs"
      )
    : [];

  const data = duboResponse
    ? duboResponse.results.map((row: any) =>
        header.reduce((acc: any, cur) => [...acc, row[cur]], [])
      )
    : [];

  return (
    <div className="max-w-5xl m-auto">
      <div className="flex flex-col">
        <div className="flex flex-row">
          <input
            value={query ?? ""}
            type="text"
            className="border w-full placeholder:gray-500 text-lg p-4 h-75"
            placeholder="Enter a query"
            onChange={(e) => {
              setQuery(e.target.value);
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                handleQuery(query);
              }
            }}
          />
          <button
            className="bg-spBlue text-white font-mono p-3"
            onClick={() => {
              handleQuery(query);
            }}
          >
            {!awaitingResult && (
              <>
                Run
                <FaPlay className="inline-block h-4 w-4" />
              </>
            )}
            {awaitingResult && <FaSpinner className="animate-spin h-4 w-4" />}
          </button>
        </div>

        {error && (
          <p className="bg-orange-500 text-white font-mono px-3 mt-3">
            {error}
          </p>
        )}
        {!awaitingResult && duboResponse && (
          <>
            <p className="font-semibold">Generated SQL</p>
            <p className="font-mono max-w-5xl whitespace-pre-wrap">
              {duboResponse.query_text}
            </p>
          </>
        )}
        {!awaitingResult && !error && duboResponse?.results && (
          <>
            <br />
            <p>Results:</p>
            <div className="overflow-scroll">
              {duboResponse.results.length > 0 && (
                <>
                  <p>{simplur`${duboResponse.results.length} row[|s] returned`}</p>
                  <DataFrameViewer header={header} data={data} />
                </>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Demos;
