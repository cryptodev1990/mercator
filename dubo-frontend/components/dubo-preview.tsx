import { useEffect, useState } from "react";
import duboQuery from "../lib/dubo-client";
import initSqlJs from "sql.js";
import DataFrameViewer from "./data-frame-viewer";
import { useLocalSqlite } from "../lib/hooks/use-sql-db";
import { FaPlay, FaSpinner } from "react-icons/fa";
import { getUploadData } from "../lib/utils";
import { DATA_OPTIONS } from "../lib/demo-data";
import simplur from "simplur";
import { CloseButton } from "./close-button";

type DataNames = keyof typeof DATA_OPTIONS;

const SuggestedQueries = ({
  queries,
  handleQuery,
  setQuery,
}: {
  queries: { query: string; sql: string }[];
  handleQuery: (sql: string) => void;
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
          }}
        >
          {query}
        </span>
      ))}
    </div>
  );
};

const DuboPreview = () => {
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState<string>("");
  const [duboResponse, setDuboResponse] = useState<string | null>(null);
  const [execResults, setExecResults] = useState<initSqlJs.QueryExecResult[]>(
    []
  );
  const [selectedData, setSelectedData] = useState<DataNames>("Fortune 500");
  const [awaitingResult, setAwaitingResult] = useState<boolean>(false);
  const [customData, setCustomData] = useState<File[] | null>(null);
  const {
    exec,
    status,
    error: sqlError,
  } = useLocalSqlite({
    urlsOrFile: customData || DATA_OPTIONS[selectedData].data,
  });

  const wrappedExec = (sql: string) => {
    const res = exec(sql);
    if (res) {
      setExecResults(res);
    } else {
      setExecResults([]);
      setError("Query returned no results.");
    }
    return res;
  };

  useEffect(() => {
    if (sqlError) {
      // TODO provide a better error message
      console.log(sqlError);
      setError((sqlError as any).message);
    }
  }, [sqlError]);

  useEffect(() => {
    if (!error) {
      return;
    }
    console.error(error);
  }, [error]);

  useEffect(() => {
    if (status === "ready") {
      let res = wrappedExec("SELECT * FROM tbl_0 LIMIT 10");
      if (res?.length === 0 || typeof res === "undefined") {
        setError("No tables found");
        return;
      }
    }
  }, [status]);

  if (error && status !== "ready") {
    return (
      <div className="flex flex-col items-center justify-center">
        <h1>Error loading data</h1>
      </div>
    );
  }

  if (status === "preparing") {
    return (
      <div className="flex flex-col items-center justify-center">
        <h1>Preparing data...</h1>
        <FaSpinner className="animate-spin h-10 w-10 text-blue-500" />
      </div>
    );
  }

  const handleQuery = async (sql: string) => {
    setAwaitingResult(true);
    setError(null);
    const schemas = exec(
      `SELECT sql FROM sqlite_schema WHERE name LIKE 'tbl_%'`
    );
    if (schemas?.length === 0 || typeof schemas === "undefined") {
      setError("No tables found");
      return;
    }
    const res = schemas[0].values.map((row: any) => row[0]);
    if (res.length === 0) {
      setError("No tables found");
      return;
    }
    const duboRes = await duboQuery(sql, res);
    if (duboRes.query_text) {
      setDuboResponse(duboRes.query_text);
      wrappedExec(duboRes.query_text);
      setAwaitingResult(false);
    } else {
      setError("Query failed. Try a different query.");
    }
  };

  return (
    <div className="max-w-5xl m-auto">
      <div className="flex flex-col">
        {customData && (
          <div className="flex flex-col gap-2">
            <h1 className="text-lg">
              Custom data <CloseButton onClick={() => setCustomData(null)} />
            </h1>
            <div className="flex flex-col gap-2"></div>
          </div>
        )}
        {!customData && (
          <>
            <select
              className="border w-full placeholder:gray-500 text-lg"
              onChange={async (e) => {
                setDuboResponse(null);
                setExecResults([]);
                setQuery("");
                if (e.target.value === "custom") {
                  const f = await getUploadData();
                  if (!f) {
                    setError("No file selected");
                    return;
                  }
                  setCustomData([f]);
                } else {
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
            value={query ?? ""}
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
        {!query && !customData && (
          <div>
            <p className="text-sm pt-4 pb-2">Some ideas:</p>
            <SuggestedQueries
              queries={DATA_OPTIONS[selectedData].queries}
              handleQuery={handleQuery}
              setQuery={setQuery}
            />
          </div>
        )}
        {error && (
          <p className="bg-orange-500 text-white font-mono px-3 mt-3">
            {error}
          </p>
        )}
        {duboResponse && (
          <>
            <p className="font-semibold">Generated SQL</p>
            <p className="font-mono max-w-5xl whitespace-pre-wrap">
              {duboResponse}
            </p>
          </>
        )}
        {!awaitingResult && !error && (
          <>
            <br />
            <p>Results:</p>
            <div className="overflow-scroll">
              {status === "ready" && execResults.length > 0 && (
                <>
                  <p>{simplur`${execResults[0]?.values.length} row[|s] returned`}</p>
                  <DataFrameViewer
                    header={execResults[0]?.columns ?? []}
                    data={execResults[0]?.values ?? []}
                  />
                </>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default DuboPreview;
