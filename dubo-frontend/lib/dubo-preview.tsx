import { use, useEffect, useState } from "react";
import duboQuery from "./dubo-client";
import initSqlJs from "sql.js";
import { DataFrameViewer } from "./DataFrameViewer";
import { useLocalSqlite } from "./use-sql-db";
import { FaPlay, FaSpinner } from "react-icons/fa";

const DATA_OPTIONS = {
  "US Census ACS 2021 Subset": [
    "https://raw.githubusercontent.com/ajduberstein/geo_datasets/master/2021_5_yr_acs.csv",
    "https://raw.githubusercontent.com/ajduberstein/geo_datasets/master/zcta-centroids.csv",
  ],
  "Fortune 500": [
    "https://raw.githubusercontent.com/ajduberstein/geo_datasets/master/fortune_500.csv",
  ],
};

type DataNames = keyof typeof DATA_OPTIONS;

export type DataFrame = {
  columns: string[];
  data: any[];
};

export async function getUploadData(): Promise<File | null> {
  const file = await new Promise((resolve) => {
    const input = document.createElement("input");
    input.type = "file";
    // restrict to csv files or json files
    input.accept = ".csv,.json";
    input.onchange = () => {
      resolve(input.files?.[0]);
    };
    input.click();
  });
  if (!file) {
    return null;
  }
  return file as File;
}

const DuboPreview = () => {
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState<string | null>(null);
  const [duboResponse, setDuboResponse] = useState<string | null>(null);
  const [execResults, setExecResults] = useState<initSqlJs.QueryExecResult[]>(
    []
  );
  const [selectedData, setSelectedData] = useState<DataNames | null>(
    "Fortune 500"
  );
  const [customData, setCustomData] = useState<File[] | null>(null);
  const {
    exec,
    status,
    error: sqlError,
  } = useLocalSqlite({
    // @ts-ignore
    urlsOrFile: customData || DATA_OPTIONS[selectedData],
  });

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
      const res = exec("SELECT * FROM tbl_0 LIMIT 10");
      if (res?.length === 0 || typeof res === "undefined") {
        setError("No tables found");
        return;
      }
      setExecResults(res);
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

  return (
    <div>
      <div className="flex flex-col min-w-5xl">
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
        <div className="flex flex-row">
          <input
            value={query ?? ""}
            type="text"
            className="border w-full placeholder:gray-500 text-lg p-4"
            placeholder="Enter a query"
            onChange={(e) => {
              setQuery(e.target.value);
            }}
          />
          <button
            className="bg-blue-500 text-white font-mono p-3"
            onClick={async () => {
              const schemas = await exec(
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
              if (query === null) {
                setError("No query found");
                return;
              }
              const duboRes = await duboQuery(query, res);
              if (duboRes.query_text) {
                setDuboResponse(duboRes.query_text);
                const res = exec(duboRes.query_text);
                if (res) {
                  setExecResults(res);
                } else {
                  setError("Query returned no results.");
                }
              } else {
                setError("Query failed. Try a different query.");
              }
            }}
          >
            Run
            <FaPlay className="inline-block h-4 w-4" />
          </button>
        </div>
        {error && (
          <p className="bg-orange-500 text-white font-mono px-3">
            Error: {error}
          </p>
        )}
        {duboResponse && (
          <>
            <p>SQL:</p>
            <p className="font-mono max-w-5xl whitespace-pre-wrap">
              {duboResponse}
            </p>
          </>
        )}
        <p>Results:</p>
        <div className="max-w-[800px] overflow-scroll">
          {status === "running" && (
            <div className="flex flex-col items-center justify-center">
              <h1>Running query...</h1>
              <FaSpinner className="animate-spin h-10 w-10 text-blue-500" />
            </div>
          )}
          {status === "ready" && execResults.length > 0 && (
            <>
              <p>{execResults[0]?.values.length} rows returned</p>
              <DataFrameViewer
                header={execResults[0]?.columns ?? []}
                data={execResults[0]?.values ?? []}
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default DuboPreview;
