import React, { useState } from "react";
import { FaPlay, FaSpinner } from "react-icons/fa";
import initSqlJs from "sql.js";
import useDuboResults from "../lib/hooks/use-dubo-results";
import DataFrameViewer from "./data-frame-viewer";
import { getUploadData } from "../lib/utils";
import { DATA_OPTIONS, DataNames } from "../lib/demo-data";
import simplur from "simplur";
import { CloseButton } from "./close-button";
import useSQLDb from "../lib/hooks/use-sql-db";
import useLoadData from "../lib/hooks/use-load-data";
import usePrepareData from "../lib/hooks/use-prepare-data";

const Results = ({
  results,
}: {
  results: initSqlJs.QueryExecResult[] | undefined;
}) => (
  <div className="animate-fadeIn100">
    <br />
    <p>Results:</p>
    <div className="overflow-scroll">
      {results && results.length > 0 && (
        <div className="animate-fadeIn100">
          <p>{simplur`${results[0]?.values.length} row[|s] returned`}</p>
          <DataFrameViewer
            header={results[0]?.columns ?? []}
            data={results[0]?.values ?? []}
          />
        </div>
      )}
    </div>
  </div>
);

const SuggestedQueries = ({
  queries,
  handleQuery,
  setDuboQuery,
  setQuery,
}: {
  queries: { query: string; sql: string }[];
  handleQuery: (sql: string) => void;
  setDuboQuery: React.Dispatch<React.SetStateAction<string>>;
  setQuery: (prompt: string) => void;
}) => {
  return (
    <div className="flex gap-1 flex-wrap">
      {queries.map(({ query, sql }, index) => (
        <span
          key={index}
          className={`
            px-2 sm:px-4 py-2 rounded sm:rounded-full border border-spBlue
            text-sm w-max cursor-pointer sm:truncate sm:text
            transition duration-300 ease bg-spBlue text-white`}
          onClick={() => {
            handleQuery(sql);
            setQuery(query);
            setDuboQuery(query);
          }}
        >
          {query}
        </span>
      ))}
    </div>
  );
};

const DuboPreview = () => {
  const [query, setQuery] = useState<string>("");
  const [duboQuery, setDuboQuery] = useState("");
  const [selectedData, setSelectedData] = useState<DataNames | null>(
    "Fortune 500"
  );
  const [customData, setCustomData] = useState<File[] | null>(null);

  const {
    db,
    error: dbError,
    loading: dbLoading,
    results,
    setResults,
  } = useSQLDb();
  const {
    dfs,
    error: prepareError,
    reset,
  } = usePrepareData({
    urlsOrFile:
      customData || (selectedData ? DATA_OPTIONS[selectedData].data : []),
    selectedData,
  });
  const {
    error: dataError,
    setError: setDataError,
    loading: dataLoading,
    setLoading: setDataLoading,
    schemas,
  } = useLoadData({
    dfs,
    db,
    setResults,
  });
  const {
    data,
    error: duboError,
    isValidating,
    mutate: setDuboResults,
  } = useDuboResults({ query: duboQuery, schemas });

  const hasError = dataError || prepareError || duboError?.message;

  if (dbError) {
    return (
      <div className="flex flex-col items-center justify-center">
        <h1>Error loading data</h1>
      </div>
    );
  }

  if (dbLoading || dataLoading) {
    return (
      <div className="flex flex-col items-center justify-center">
        <h1>Preparing data...</h1>
        <FaSpinner className="animate-spin h-10 w-10 text-blue-500" />
      </div>
    );
  }

  const handleQuery = (sql: string) => {
    const res = db?.exec(sql);
    if (res) {
      setResults(res);
    } else {
      setResults([]);
    }
    return res;
  };

  return (
    <div className="max-w-5xl m-auto">
      <div className="flex flex-col">
        {customData && (
          <div className="flex flex-col gap-2">
            <h1 className="text-lg">
              Custom data{" "}
              <CloseButton
                onClick={() => {
                  setSelectedData("Fortune 500");
                  setCustomData(null);
                  setDataError(null);
                  reset();
                }}
              />
            </h1>
            <div className="flex flex-col gap-2"></div>
          </div>
        )}
        {!customData && (
          <>
            <select
              className="border w-full placeholder:gray-500 text-lg"
              onChange={async (e) => {
                setDuboResults(null);
                setDuboQuery("");
                setQuery("");
                if (e.target.value === "custom") {
                  const f = await getUploadData();
                  if (f) {
                    setCustomData([f]);
                    setSelectedData(null);
                  }
                } else {
                  setDataLoading(true);
                  setSelectedData(e.target.value as any);
                }
              }}
              value={typeof selectedData === "string" ? selectedData : "Custom"}
            >
              {Object.keys(DATA_OPTIONS).map((key) => (
                <option key={key} value={key}>
                  {key}
                </option>
              ))}
              <option key={"custom"} value={"custom"}>
                Upload your own data
              </option>
            </select>
          </>
        )}
        <div className="flex flex-row">
          <input
            value={query}
            type="text"
            className="border w-full placeholder:gray-500 text-lg p-4"
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
        {!query && !customData && selectedData && (
          <div>
            <p className="text-sm pt-4 pb-2">Some ideas:</p>
            <SuggestedQueries
              queries={DATA_OPTIONS[selectedData].queries}
              handleQuery={handleQuery}
              setDuboQuery={setDuboQuery}
              setQuery={setQuery}
            />
          </div>
        )}
        {hasError && (
          <p className="bg-orange-500 text-white font-mono px-3 mt-3">
            {hasError}
          </p>
        )}
        {data && (
          <div className="animate-fadeIn100">
            <p className="font-semibold">Generated SQL</p>
            <p className="font-mono max-w-5xl whitespace-pre-wrap">
              {data.query_text}
            </p>
          </div>
        )}
        {!isValidating && !hasError && <Results results={results} />}
      </div>
    </div>
  );
};

export default DuboPreview;
