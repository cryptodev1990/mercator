import clsx from "clsx";
import { useEffect, useRef, useState } from "react";
import {
  selectSearchState,
  setInputText,
} from "../../../../src/search/search-slice";
import { useDispatch, useSelector } from "react-redux";
import { useOsmQueryGetQuery } from "src/store/search-api";
import {
  addNewLayer,
  runNewSearch,
} from "src/lib/cross-slice-actions/add-new-layer";

const SearchBar = () => {
  const focusRef = useRef<HTMLInputElement>(null);
  // within-component copy of query text
  const { inputText } = useSelector(selectSearchState);
  const [localInputText, setLocalInputText] = useState<string>(inputText || "");
  const [timeElapsed, setTimeElapsed] = useState<number>(0);
  const { data, isSuccess, isLoading } = useOsmQueryGetQuery(
    {
      query: inputText || "",
    },
    {
      skip: (inputText?.length ?? false) > 0 ? false : true,
    }
  );
  const dispatch = useDispatch();

  useEffect(() => {
    if (isSuccess) {
      addNewLayer(data, dispatch);
    }
  }, [isLoading, isSuccess, data, dispatch]);

  useEffect(() => {
    if (focusRef.current) {
      focusRef.current.focus();
    }
  }, []);

  useEffect(() => {
    // if the query is loading, start the timer
    let interval: NodeJS.Timeout;
    if (isLoading) {
      setTimeElapsed(0);
      interval = setInterval(() => {
        setTimeElapsed((prev) => prev + 1);
      }, 1000);
    }
    return () => {
      clearInterval(interval);
    };
  }, [isLoading]);

  return (
    <div className="flex flex-col justify-start items-center space-y-10">
      <div className="border border-slate-200 rounded h-12 px-4 z-10 w-full bg-slate-200 relative flex flex-row">
        <div className="absolute top-0 left-0 flex flex-row m-0 p-0 h-full w-full">
          <input
            ref={focusRef}
            value={localInputText || ""}
            id="search"
            placeholder="Start typing to search..."
            className="w-full h-full bg-transparent pl-2 text-black outline-none"
            onKeyDown={(e) => {
              /* STEP 1: User runs a query */
              // Non-intuitive stuff here -- do I really need to use dispatch in the component?
              if (e.key === "Enter") {
                runNewSearch(localInputText, dispatch);
              }
            }}
            onChange={(e) => {
              setLocalInputText(e.target.value);
            }}
          />
          <button
            className={clsx(
              "p-1 px-5 bg-purple-500 rounded w-40 h-full text-white",
              isLoading && "animate-pulse"
            )}
            onClick={(e) => {
              runNewSearch(localInputText, dispatch);
            }}
          >
            {isLoading ? `${timeElapsed} sec` : "Locate"}
          </button>
        </div>
      </div>
    </div>
  );
};
export default SearchBar;
