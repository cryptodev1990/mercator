import CodeMirror from "@uiw/react-codemirror";
import { sql } from "@codemirror/lang-sql";
import * as events from "@uiw/codemirror-extensions-events";
import { format } from "sql-formatter";
import { githubLight } from "@uiw/codemirror-theme-github";
import { useState, Dispatch, SetStateAction } from "react";

const SQLEditor = ({
  query,
  exec,
  resultsError,
  setResultsError,
}: {
  query: string;
  exec: (sql: string) => void;
  resultsError: string | null;
  setResultsError: Dispatch<SetStateAction<string | null>>;
}) => {
  const [value, setValue] = useState(format(query));
  const [isCtrlMetaKeyDown, setIsCtrlMetaKeyDown] = useState(false);

  const eventExtenstion = events.content({
    keypress: (e) => {
      if (e.key === "Enter" && isCtrlMetaKeyDown) {
        setResultsError(null);
        exec(value);
      }
    },
    keydown: (e) => {
      if (e.key === "Control" || e.key === "Meta") {
        setIsCtrlMetaKeyDown(true);
      }

      if (e.key === "Enter" && isCtrlMetaKeyDown) {
        setResultsError(null);
        exec(value);
      }
    },
    keyup: (e) => {
      if (e.key === "Control" || e.key === "Meta") {
        setIsCtrlMetaKeyDown(false);
      }
    },
  });

  return (
    <div className="mt-6 animate-fadeIn100">
      <div className="flex justify-between">
        <p className="text-lg">Generated SQL:</p>
        {(format(query) !== value || resultsError) && (
          <div className="flex gap-2">
            <button
              onClick={() => {
                setResultsError(null);
                setValue(format(query));
                exec(query);
              }}
              className="inline-block px-3 py-1 border border-spBlue text-spBlue font-medium text-sm leading-tight hover:bg-gray-100 focus:bg-gray-100 transition duration-150 ease-in-out"
            >
              Reset
            </button>
            <button
              onClick={() => {
                setResultsError(null);
                exec(value);
              }}
              className="inline-block px-3 py-1 border border-spBlue text-spBlue font-medium text-sm leading-tight hover:bg-gray-100 focus:bg-gray-100 transition duration-150 ease-in-out"
            >
              Re-run query
            </button>
          </div>
        )}
      </div>
      <div className="max-w-5xl mt-2">
        <CodeMirror
          value={value}
          extensions={[sql(), eventExtenstion]}
          basicSetup={{
            foldGutter: false,
            autocompletion: false,
            defaultKeymap: false,
          }}
          theme={githubLight}
          minHeight="200"
          onChange={(value: string) => setValue(value)}
        />
      </div>
    </div>
  );
};

export default SQLEditor;
