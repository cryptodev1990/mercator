import { useState } from "react";
import DataFrameViewer from "./data-frame-viewer";
import { FaPlay, FaSpinner } from "react-icons/fa";
import simplur from "simplur";
import useDuboResults from "../lib/hooks/use-dubo-results";

const Demos = ({ databaseSchema }: { databaseSchema: DatabaseSchema }) => {
  const [query, setQuery] = useState<string>(
    "Show ten rows of data from the transactions table"
  );

  const [duboQuery, setDuboQuery] = useState<string>(
    "Show ten rows of data from the transactions table"
  );

  const { data, error, isValidating } = useDuboResults({
    query: duboQuery,
    databaseSchema,
  });

  const header = data
    ? Object.keys(data?.results[0]).filter(
        (c) => c !== "inputs" && c !== "outputs"
      )
    : [];

  const rows = data
    ? data.results.map((row: any) =>
        header.reduce((acc: any, cur) => [...acc, row[cur]], [])
      )
    : [];

  return (
    <div className="max-w-5xl m-auto">
      <div className="flex flex-col">
        <div className="flex flex-row">
          <input
            value={query}
            type="text"
            className="border w-full placeholder:gray-500 text-lg p-4 h-75"
            placeholder="Enter a query"
            onChange={(e) => {
              setQuery(e.target.value);
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                setDuboQuery(query);
              }
            }}
          />
          <button
            className="bg-spBlue text-white font-mono p-3"
            onClick={() => {
              setDuboQuery(query);
            }}
          >
            {!isValidating && (
              <>
                Run
                <FaPlay className="inline-block h-4 w-4" />
              </>
            )}
            {isValidating && <FaSpinner className="animate-spin h-4 w-4" />}
          </button>
        </div>

        {error && (
          <p className="bg-orange-500 text-white font-mono px-3 mt-3">
            {error.message}
          </p>
        )}
        {!isValidating && data && (
          <>
            <p className="font-semibold">Generated SQL</p>
            <p className="font-mono max-w-5xl whitespace-pre-wrap">
              {data.query_text}
            </p>
          </>
        )}
        {!isValidating && !error && data?.results && (
          <>
            <br />
            <p>Results:</p>
            <div className="overflow-scroll">
              {data.results.length > 0 && (
                <>
                  <p>{simplur`${data.results.length} row[|s] returned`}</p>
                  <DataFrameViewer header={header} data={rows} />
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
