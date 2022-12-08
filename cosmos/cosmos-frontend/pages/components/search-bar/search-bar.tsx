import clsx from "clsx";
import { useEffect, useRef, useState } from "react";
import {
  selectSearchState,
  setInputText,
} from "../../../src/search/search-slice";
import { useDispatch, useSelector } from "react-redux";
import { useOsmQueryGetQuery } from "src/store/search-api";
import { addNewLayer } from "src/lib/add-new-layer";

const SearchBar = () => {
  const focusRef = useRef<HTMLInputElement>(null);
  // within-component copy of query text
  const { inputText } = useSelector(selectSearchState);
  const [localInputText, setLocalInputText] = useState<string>(inputText || "");
  const [timeElapsed, setTimeElapsed] = useState<number>(0);
  const { data, isSuccess, isLoading } = useOsmQueryGetQuery(
    {
      query: inputText || "",
      limit: 10000,
    },
    {
      skip: (inputText?.length ?? false) > 0 ? false : true,
    }
  );
  const dispatch = useDispatch();

  useEffect(() => {
    // if the query is successful, clear the query and append the results
    if (isSuccess) {
      addNewLayer(data, dispatch);
    }
  }, [isSuccess, data, dispatch]);

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
              if (e.key === "Enter") {
                dispatch(setInputText(e.currentTarget.value));
              }
            }}
            onChange={(e) => {
              setLocalInputText(e.currentTarget.value);
            }}
          />
          <button
            className={clsx(
              "p-1 px-5 bg-purple-500 rounded w-40 h-full text-white",
              isLoading && "animate-pulse"
            )}
            onClick={(e) => {
              dispatch(setInputText(localInputText));
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
