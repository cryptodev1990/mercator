import clsx from "clsx";
import { useEffect, useMemo, useRef, useState } from "react";
import { BsDice3 } from "react-icons/bs";
import { FaSearch } from "react-icons/fa";

import { useTheme } from "../../lib/hooks/census/use-theme";
import {
  useFirstTimeSearch,
  EXAMPLES,
} from "../../lib/hooks/census/use-first-time-search";
import { useUrlState } from "../../lib/hooks/url-state/use-url-state";

import { MapToggle } from "./map-toggle";

const SearchBar = ({
  setShowErrorBox,
  value = "",
  onChange,
  onEnter,
  autocompleteSuggestions = [],
}: {
  setShowErrorBox: any;
  value: string;
  onChange: (text: string) => void;
  onEnter: (optionalSubmission?: string) => void;
  autocompleteSuggestions?: string[];
}) => {
  const { theme } = useTheme();
  const { currentStateFromUrl } = useUrlState();
  const [isFocused, setIsFocused] = useState(false);
  const [selectedSuggestion, setSelectedSuggestion] = useState(-1);
  const searchBarRef = useRef<HTMLInputElement | null>(null);

  const { placeholderExample, turnOffDemo, isFirstTimeUse } =
    useFirstTimeSearch();

  useEffect(() => {
    const urlState = currentStateFromUrl();
    if (urlState?.userQuery) {
      onChange(urlState.userQuery);
      onEnter();
      turnOffDemo();
    }
  }, []);

  const shouldDisplay = useMemo(() => {
    return (
      autocompleteSuggestions &&
      autocompleteSuggestions.length > 0 &&
      isFocused &&
      value.length > 0 &&
      value.length < 30 &&
      autocompleteSuggestions[selectedSuggestion] !== value
    );
  }, [autocompleteSuggestions, value, isFocused, selectedSuggestion]);

  return (
    <div
      className={clsx(
        theme.bgColor,
        "rounded-md relative flex flex-row justify-between"
      )}
    >
      {/* search bar input */}
      <input
        type="text"
        className={clsx(
          theme.bgColor,
          "relative bg-transparent border-none h-12 z-10 ease-in duration-300 flex-1",
          "shadow-md sm:p-3 p-1 sm:text-lg text-xs w-10/12",
          "pointer-events-auto select-all sm:select-auto",
          "focus:outline-none",
          isFirstTimeUse && "placeholder:animate-fadeIn500"
        )}
        ref={searchBarRef}
        onFocus={() => {
          setIsFocused(true);
          turnOffDemo();
        }}
        value={value}
        onChange={(e) => {
          onChange(e.target.value);
          setSelectedSuggestion(-1);
        }}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            onChange(autocompleteSuggestions[selectedSuggestion]);
            onEnter();
            setSelectedSuggestion(-1);
          }
          if (e.key === "Tab" && shouldDisplay) {
            e.preventDefault();
            onChange(autocompleteSuggestions[selectedSuggestion]);
            setSelectedSuggestion(-1);
          }
          if (e.key === "ArrowDown" && shouldDisplay) {
            setSelectedSuggestion(
              (prev) => (prev + 1) % autocompleteSuggestions.length
            );
          }
          if (e.key === "ArrowUp" && shouldDisplay) {
            setSelectedSuggestion(
              (prev) => (prev - 1) % autocompleteSuggestions.length
            );
          }
        }}
        placeholder={
          isFirstTimeUse ? placeholderExample : "What do you want to know?"
        }
      />
      <div className="flex">
        {/* search button */}
        <button
          className={clsx(
            "rounded-r-sm shadow-md hover:shadow-lg sm:w-24 w-12 h-12",
            "flex flex-row justify-center items-center space-x-2 p-2 group",
            "cursor-pointer bg-spBlue",
            theme.secondaryFontColor
          )}
          onClick={(e) => {
            onEnter();
            setShowErrorBox(false);
          }}
        >
          <div className="hover:animate-spin pointer-events-none group-hover:translate-y-[-3px]">
            <FaSearch />
          </div>
        </button>

        {/* style toggle */}
        <div className="hidden sm:block">
          <MapToggle />
        </div>
        {/* Random search button */}
        <button
          className={clsx(
            "hover:animate-moveThroughRainbow2s group-focus:hidden",
            "shadow-md h-12 w-12 hover:shadow-lg",
            "flex flex-row justify-center items-center space-x-2 p-2 rounded-r-md",
            "cursor-pointer",
            theme.secondaryBgColor,
            theme.secondaryFontColor
          )}
          onClick={(e) => {
            let randomIndex = Math.floor(Math.random() * EXAMPLES.length);
            // query can't equal the query in the search bar
            while (EXAMPLES[randomIndex] === value) {
              randomIndex = Math.floor(Math.random() * EXAMPLES.length);
            }
            onChange(EXAMPLES[randomIndex]);
            onEnter(EXAMPLES[randomIndex]);
          }}
        >
          <div className="hover:animate-spin pointer-events-none">
            <BsDice3 />
          </div>
        </button>
      </div>

      {/* autocomplete suggestions */}
      <div
        className={clsx(
          "absolute rounded-b-md shadow-md italic border-r ease-in duration-300 translate-y-12",
          shouldDisplay ? "block w-[calc(100%_-_12rem)]" : "hidden",
          theme.bgColor,
          theme.fontColor
        )}
      >
        {autocompleteSuggestions?.length > 0 &&
          autocompleteSuggestions.map((suggestion, i) => (
            <button
              key={i}
              className={clsx(
                "transition w-full text-left p-2 hover:-translate-y-1",
                theme.bgColor,
                theme.fontColor,
                i === selectedSuggestion && theme.secondaryBgColor,
                i === selectedSuggestion && theme.secondaryFontColor
              )}
              onClick={(e) => {
                onChange(suggestion);
                onEnter(suggestion);
                setIsFocused(false);
              }}
            >
              {value.length > 5 &&
                suggestion.split(value).map((part, i) => (
                  <span key={i}>
                    {i === 0 && (
                      <span className="pointer-events-auto">...</span>
                    )}
                    <span className="pointer-events-auto">{part}</span>
                  </span>
                ))}
              {value.length <= 5 && (
                <span className="pointer-events-auto">{suggestion}</span>
              )}
            </button>
          ))}
      </div>
    </div>
  );
};

export default SearchBar;
