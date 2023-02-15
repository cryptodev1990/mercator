import { useEffect, useState } from "react";
import { FaPlay, FaSpinner } from "react-icons/fa";
import { useRouter } from "next/router";
import useDuboResultsWithSchemas from "../lib/hooks/use-dubo-results-with-schemas";
import { getUploadData } from "../lib/utils";
import { DATA_OPTIONS, DataNames } from "../lib/demo-data";
import DataTable from "./data-table";
import { CloseButton } from "./close-button";
import useSQLDb from "../lib/hooks/use-sql-db";
import useLoadData from "../lib/hooks/use-load-data";
import usePrepareData from "../lib/hooks/use-prepare-data";
import SuggestedQueries from "./suggested-queries";
import SQLEditor from "./sql-editor";

const DuboPreview = ({ includeSample }: { includeSample: boolean }) => {
  const [query, setQuery] = useState<string>("");
  const [duboQuery, setDuboQuery] = useState("");
  const [selectedData, setSelectedData] = useState<DataNames | null>(
    "Fortune 500"
  );
  const [customData, setCustomData] = useState<File[] | null>(null);

  const {
    db,
    exec,
    loadError,
    loading: dbLoading,
    results,
    setResults,
    setResultsError,
    resultsError,
  } = useSQLDb();
  const {
    dfs,
    error: prepareError,
    setDfs,
    setError: setPrepareError,
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
    sample,
  } = useLoadData({
    dfs,
    db,
    setResults,
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

  const hasError =
    prepareError || dataError || resultsError || duboError?.message;

  useEffect(() => {
    if (data && data.query_text && !isLoading) {
      const duboGeneratedSql = data.query_text;
      exec(duboGeneratedSql);
    }
  }, [duboQuery, isLoading]);

  if (loadError) {
    return (
      <p
        className="bg-red-100 py-3 px-4 mb-4 mt-6 text-base text-red-700"
        role="alert"
      >
        Something went wrong loading the database. Reload the page to try again.
      </p>
    );
  }

  if (dbLoading || dataLoading) {
    return (
      <div className="flex flex-col items-center justify-center">
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
        {!isValidating && !hasError && results && results.length > 0 && (
          <DataTable results={results} showVis={showVis} />
        )}
      </div>
    </div>
  );
};

export default DuboPreview;
