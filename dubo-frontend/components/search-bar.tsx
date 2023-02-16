import clsx from "clsx";
import { useMemo, useRef, useState } from "react";
import { BsDice3 } from "react-icons/bs";
import { FaSearch } from "react-icons/fa";

import { useTheme } from "../lib/hooks/census/use-theme";
import {
  useFirstTimeSearch,
  EXAMPLES,
} from "../lib/hooks/census/use-first-time-search";

import { MapToggle } from "./geomap/map-toggle";

export const SearchBar = ({
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
  const [isFocused, setIsFocused] = useState(false);
  const [selectedSuggestion, setSelectedSuggestion] = useState(-1);
  const searchBarRef = useRef<HTMLInputElement | null>(null);

  const { placeholderExample, turnOffDemo, isFirstTimeUse } =
    useFirstTimeSearch();

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
    <div className={clsx(theme.bgColor, "flex flex-row")}>
      {/* search bar input */}
      <input
        type="text"
        className={clsx(
          "bg-transparent border-none w-full border-b-red-400",
          "w-full rounded-l-md rounded-r-none mx-auto shadow-md sm:p-3 sm:text-md p-1 text-sm",
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
      {/* search button */}
      <button
        className={clsx(
          "rounded-r-sm shadow-md hover:shadow-lg w-24 h-12",
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
      <MapToggle />
      {/* Random search button */}
      <button
        className={clsx(
          "hover:animate-moveThroughRainbow2s",
          "shadow-md w-24 h-12 sm:w-12 hover:shadow-lg",
          "flex flex-row justify-center items-center space-x-2 p-2",
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

      {/* autocomplete suggestions */}
      <div
        className={clsx(
          "absolute rounded-b-md shadow-md flex flex-col justify-start align-top text-left w-full max-w-[52rem]",
          shouldDisplay ? "block" : "hidden",
          theme.bgColor,
          theme.fontColor
        )}
        style={{
          width: searchBarRef.current?.offsetWidth,
          top: (searchBarRef.current?.offsetTop ?? 0) + 40,
        }}
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
