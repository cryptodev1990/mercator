import { useEffect, useState } from "react";
import duboQuery from "./dubo-client";
import initSqlJs from "sql.js";
import { DataFrameViewer } from "./DataFrameViewer";
import { useLocalSqlite } from "./use-sql-db";
import { FaPlay, FaSpinner } from "react-icons/fa";

const DATA_OPTIONS = {
  "US Census ACS 2021 Subset": {
    data: [
      "https://raw.githubusercontent.com/ajduberstein/geo_datasets/master/2021_5_yr_acs.csv",
      "https://raw.githubusercontent.com/ajduberstein/geo_datasets/master/zcta-centroids.csv",
    ],
    queries: [
      {
        query: "Which zip codes have the most old people and children?",
        sql: "SELECT tbl_0.zip_code, (tbl_0.elderly_pop + tbl_0.pop_under_5_years + tbl_0.pop_5_to_9_years + tbl_0.pop_10_to_14_years + tbl_0.pop_15_to_19_years) AS total_old_and_children FROM tbl_0 INNER JOIN tbl_1 ON tbl_0.zip_code = tbl_1.zcta ORDER BY total_old_and_children DESC;",
      },
    ],
  },
  "Fortune 500": {
    data: [
      "https://raw.githubusercontent.com/ajduberstein/geo_datasets/master/fortune_500.csv",
    ],
    queries: [
      {
        query:
          "Which companies are within a 50 mile radius of Washington D.C.?",
        sql: "SELECT * FROM tbl_0 WHERE (3959 * acos(cos(radians(38.9072)) * cos(radians(latitude)) * cos(radians(longitude) - radians(-77.0369)) + sin(radians(38.9072)) * sin(radians(latitude)))) < 50;",
      },
      {
        query:
          "Which companies are not located within a 150 mile radius of any other company?",
        sql: "SELECT tbl_0.name FROM tbl_0 WHERE NOT EXISTS (SELECT * FROM tbl_0 tbl_1 WHERE tbl_0.name != tbl_1.name AND (6371 * acos(cos(radians(tbl_0.latitude)) * cos(radians(tbl_1.latitude)) * cos(radians(tbl_1.longitude) - radians(tbl_0.longitude)) + sin(radians(tbl_0.latitude)) * sin(radians(tbl_1.latitude)))) < 150);",
      },
    ],
  },
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

const SuggestedQueries = ({
  queries,
  handleQuery,
}: {
  queries: { query: string; sql: string }[];
  handleQuery: (sql: string) => void;
}) => {
  const [selectedQuery, setSelectedQuery] = useState<number | null>(null);

  return (
    <div className="mt-2 flex gap-1 flex-wrap">
      {queries.map(({ query, sql }, index) => (
        <span
          key={index}
          className={`px-4 py-2 rounded-full border border-spBlue ${
            selectedQuery === index
              ? "bg-white text-spBlue"
              : "bg-spBlue text-white"
          } font-semibold text-sm w-max cursor-pointer whitespace-nowrap overflow-hidden text-ellipsis transition duration-300 ease`}
          onClick={() => {
            setSelectedQuery(index);
            handleQuery(sql);
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
  const [customData, setCustomData] = useState<File[] | null>(null);
  const {
    exec,
    status,
    error: sqlError,
  } = useLocalSqlite({
    urlsOrFile: customData || DATA_OPTIONS[selectedData].data,
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

  const handleQuery = async (sql: string) => {
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
    const duboRes = await duboQuery(sql, res);
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
  };

  return (
    <div className="max-w-5xl m-auto">
      <div className="flex flex-col">
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
            className="bg-spBlue text-white font-mono p-3"
            onClick={() => handleQuery(query)}
          >
            Run
            <FaPlay className="inline-block h-4 w-4" />
          </button>
        </div>
        <SuggestedQueries
          queries={DATA_OPTIONS[selectedData].queries}
          handleQuery={handleQuery}
        />
        {error && (
          <p className="bg-orange-500 text-white font-mono px-3 mt-3">
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
        <div className="overflow-scroll">
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
