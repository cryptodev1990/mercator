import { useState } from "react";
import { DataTable } from "./data-table";
import { FaPlay, FaSpinner } from "react-icons/fa";
import useDuboResults from "../lib/hooks/use-dubo-results";
import SQL from "./sql";

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
          <p
            className="bg-red-100 py-3 px-4 mb-4 mt-6 text-sm text-red-700"
            role="alert"
          >
            {error.message}
          </p>
        )}
        {!isValidating && data?.query_text && (
          <div className="mt-6 animate-fadeIn100">
            <p className="text-lg">Generated SQL:</p>
            <div className="max-w-5xl mt-2">
              <SQL query={data.query_text} light />
            </div>
          </div>
        )}
        {!isValidating &&
          !error &&
          data?.results &&
          data.results.length > 0 && (
            <DataTable
              rows={data.results}
              columns={Object.keys(data?.results[0])
                .filter((c) => c !== "inputs" && c !== "outputs")
                .map((c) => ({ field: c }))}
            />
          )}
        {data?.error && (
          <p
            className="bg-red-100 py-3 px-5 text-sm text-red-700 mt-6"
            role="alert"
          >
            {data.error}
          </p>
        )}
      </div>
    </div>
  );
};

export default Demos;
