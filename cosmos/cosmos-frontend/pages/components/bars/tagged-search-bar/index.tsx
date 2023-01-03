import clsx from "clsx";
import { useContext, useEffect, useState } from "react";
import { useSelector } from "react-redux";
import TaggedIntent from "./tagged-intent";
import { selectSearchState } from "src/search/search-slice";
import AnalysisUIContext from "../../../../src/contexts/analysis-context";

const TaggedSearchBar = () => {
  const { searchResults } = useSelector(selectSearchState);

  const ctx = useContext(AnalysisUIContext);

  const [timeElapsed, setTimeElapsed] = useState<number>(0);
  const isLoading = false;

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

  if (!searchResults || !ctx.selectedIntentResponse) {
    return null;
  }

  return (
    <div className="flex flex-col justify-start items-center space-y-10">
      <div className="rounded h-12 px-4 z-10 w-full relative flex flex-row">
        <div className="absolute top-0 left-0 flex flex-row m-0 p-0 h-full w-full gap-2">
          <TaggedIntent ir={ctx.selectedIntentResponse} />
          <button
            className={clsx(
              "flex-none ml-auto p-1 px-5 bg-purple-500 rounded w-40 h-full text-slate-50",
              isLoading && "animate-pulse"
            )}
            onClick={(e) => {
              console.log("Locate button clicked");
            }}
          >
            {isLoading ? `${timeElapsed} sec` : "Locate"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default TaggedSearchBar;
