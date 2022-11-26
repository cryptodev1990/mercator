import clsx from "clsx";
import { useEffect, useRef, useState } from "react";
import { useOsmQueryGetQuery } from "src/store/search-api";
import { appendSearchResult } from "@/pages/components/state/search-slice";
import { setInputText, selectSearchState } from "../state/search-slice";
import { useDispatch, useSelector } from "react-redux";

const CancelButton = () => {
  return (
    <div className="cursor-pointer" onClick={() => {}}>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="h-6 w-6"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M6 18L18 6M6 6l12 12"
        />
      </svg>
    </div>
  );
};

const SearchBar = () => {
  const focusRef = useRef<HTMLInputElement>(null);
  const [query, setQuery] = useState<string>("");
  const { data, error, isLoading, isSuccess } = useOsmQueryGetQuery(
    { query },
    { skip: !query }
  );

  const dispatch = useDispatch();
  const { inputText } = useSelector(selectSearchState);

  useEffect(() => {
    if (focusRef.current) {
      focusRef.current.focus();
    }
  }, []);

  useEffect(() => {
    if (isSuccess && query && data) {
      console.log(data);
      dispatch(appendSearchResult(data));
      dispatch(setInputText(""));
      setQuery("");
    }
  }, [isSuccess, query]);

  return (
    <div className="flex flex-col justify-start items-center w-[80vw] m-auto space-y-10">
      <div className="border border-slate-200 rounded h-12 px-4 z-10 w-full bg-slate-200 relative flex flex-row">
        <div className="absolute top-0 left-0 flex flex-row m-0 p-0 h-full w-full">
          <input
            ref={focusRef}
            value={inputText || ""}
            placeholder="Start typing to search..."
            className="w-full h-full bg-transparent pl-2 text-black outline-none"
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                setQuery(inputText || "");
              }
            }}
            onChange={(e) => {
              dispatch(setInputText(e.currentTarget.value));
            }}
          />
          <button
            className={clsx(
              "p-1 px-5 bg-purple-500 rounded",
              isLoading && "animate-pulse"
            )}
            onClick={(e) => {
              setQuery(inputText || "");
            }}
          >
            {isLoading ? "Loading..." : "Locate"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default SearchBar;
