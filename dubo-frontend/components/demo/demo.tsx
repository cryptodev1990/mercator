import { useEffect, useState } from "react";
import { FaPlay, FaSpinner } from "react-icons/fa";
import { useRouter } from "next/router";

import useDuboResultsWithSchemas from "../../lib/hooks/use-dubo-results-with-schemas";
import { DATA_OPTIONS } from "../../lib/demo-data";
import useLoadData from "../../lib/hooks/use-load-data";
import useSanitizeData from "../../lib/hooks/use-sanitize-data";
import DataTable from "../data-table";

import Visualizer from "./visualizer";
import SuggestedQueries from "./suggested-queries";
import SQLEditor from "./sql-editor";

const Demo = ({
  includeSample,
  urlsOrFile,
  selectedData,
}: {
  selectedData: SampleDataKey | null;
  includeSample: boolean;
  urlsOrFile: (string | File)[] | null;
}) => {
  const [query, setQuery] = useState("");
  const [duboQuery, setDuboQuery] = useState("");
  const [rows, setRows] = useState<object[] | null>(null);
  const [columns, setColumns] = useState<object[] | null>(null);

  useEffect(() => {
    setQuery("");
    setDuboQuery("");
  }, [urlsOrFile]);

  const { dfs, error: prepareError } = useSanitizeData({
    urlsOrFile,
  });
  const {
    exec,
    error: dataError,
    loading: dataLoading,
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
  } = useDuboResultsWithSchemas({
    query: duboQuery,
    schemas,
    dataSample: includeSample ? sample : undefined,
  });

  const router = useRouter();
  const showVis = router.query?.vis !== undefined;

  const hasError = resultsError || duboError?.message;

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
        className="max-w-5xl m-auto bg-red-100 py-3 px-4 mb-4 mt-6 text-base text-red-700 animate-fadeIn100"
        role="alert"
      >
        Something went wrong loading the database. Reload the page to try again.
      </p>
    );
  }

  if (prepareError) {
    return (
      <p
        className="max-w-5xl m-auto bg-red-100 py-3 px-4 mb-4 mt-6 text-base text-red-700 animate-fadeIn100"
        role="alert"
      >
        {prepareError}
      </p>
    );
  }

  if (dataLoading) {
    return (
      <div className="flex flex-col items-center justify-center animate-fadeIn100 min-h-[300px]">
        <h6 className="text-lg leading-tight mb-4">Preparing data...</h6>
        <FaSpinner className="animate-spin h-10 w-10 text-spBlue" />
      </div>
    );
  }

  return (
    <div className="max-w-5xl m-auto animate-fadeIn100">
      <div className="flex flex-col">
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
        {!query && selectedData && (
          <div>
            <p className="text-lg pt-4 pb-2">Some ideas:</p>
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

export default Demo;
