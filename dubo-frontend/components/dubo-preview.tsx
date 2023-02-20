import { useEffect, useState } from "react";
import { FaPlay, FaSpinner } from "react-icons/fa";
import { useRouter } from "next/router";

import useDuboResultsWithSchemas from "../lib/hooks/use-dubo-results-with-schemas";
import { getFileFromUpload } from "../lib/utils";
import { DATA_OPTIONS, DataNames } from "../lib/demo-data";
import useLoadData from "../lib/hooks/use-load-data";
import useSanitizeData from "../lib/hooks/use-sanitize-data";

import DataTable from "./data-table";
import { CloseButton } from "./close-button";
import Visualizer from "./visualizer";
import SuggestedQueries from "./suggested-queries";
import SQLEditor from "./sql-editor";

const DuboPreview = ({ includeSample }: { includeSample: boolean }) => {
  const [query, setQuery] = useState<string>("");
  const [duboQuery, setDuboQuery] = useState("");
  const [selectedData, setSelectedData] = useState<DataNames | null>(
    "Fortune 500"
  );
  const [customData, setCustomData] = useState<File[] | null>(null);
  const [rows, setRows] = useState<object[] | null>(null);
  const [columns, setColumns] = useState<object[] | null>(null);

  const {
    dfs,
    error: prepareError,
    setDfs,
    setError: setPrepareError,
  } = useSanitizeData({
    urlsOrFile:
      customData || (selectedData ? DATA_OPTIONS[selectedData].data : []),
    selectedData,
  });
  const {
    exec,
    error: dataError,
    setError: setDataError,
    loading: dataLoading,
    setLoading: setDataLoading,
    schemas,
    sample,
    results,
    resultsError,
    setResultsError,
  } = useLoadData({
    dfs,
  });
  const {
    data,
    error: duboError,
    isValidating,
    isLoading,
    mutate: setDuboResults,
  } = useDuboResultsWithSchemas({
    query: duboQuery,
    schemas,
    dataSample: includeSample ? sample : undefined,
  });

  const router = useRouter();
  const showVis = router.query?.vis !== undefined;

  const hasError = prepareError || resultsError || duboError?.message;

  useEffect(() => {
    if (data && data.query_text && !isLoading) {
      const duboGeneratedSql = data.query_text;
      exec(duboGeneratedSql);
    }
  }, [duboQuery, isLoading]);

  useEffect(() => {
    if (results) {
      const res = results[0];
      if (res) {
        const { values, columns } = res;

        setRows(
          values.map((row) =>
            columns.reduce((acc, c, index) => ({ ...acc, [c]: row[index] }), {})
          )
        );
        setColumns(columns.map((c) => ({ field: c })));
      }
    }
  }, [results]);

  if (dataError) {
    return (
      <p
        className="bg-red-100 py-3 px-4 mb-4 mt-6 text-base text-red-700 animate-fadeIn100"
        role="alert"
      >
        Something went wrong loading the database. Reload the page to try again.
      </p>
    );
  }

  if (dataLoading) {
    return (
      <div className="flex flex-col items-center justify-center animate-fadeIn100">
        <h1>Preparing data...</h1>
        <FaSpinner className="animate-spin h-10 w-10 text-spBlue" />
      </div>
    );
  }

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
                  setDfs(undefined);
                  setPrepareError(null);
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
                  const f = await getFileFromUpload();
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
        {!query && !customData && selectedData && (
          <div>
            <p className="text-md pt-4 pb-2">Some ideas:</p>
            <SuggestedQueries
              queries={DATA_OPTIONS[selectedData].queries}
              handleSqlQuery={exec}
              setDuboQuery={setDuboQuery}
              setQuery={setQuery}
            />
          </div>
        )}
        {hasError && (
          <p
            className="bg-red-100 py-3 px-4 mb-4 mt-6 text-sm text-red-700"
            role="alert"
          >
            {hasError}
          </p>
        )}
        {data && (
          <SQLEditor
            query={data.query_text}
            exec={exec}
            setResultsError={setResultsError}
            resultsError={resultsError}
          />
        )}
        {!isValidating && !hasError && (
          <>
            {rows && rows.length > 0 && columns && columns?.length > 0 && (
              <DataTable rows={rows} columns={columns} />
            )}
            {results && showVis && (
              <Visualizer
                header={results[0]?.columns ?? []}
                data={results[0]?.values ?? []}
              />
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default DuboPreview;
