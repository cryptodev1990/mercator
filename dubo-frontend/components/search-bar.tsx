import clsx from "clsx";
import { useMemo, useRef, useState } from "react";
import { useTheme } from "../lib/hooks/census/use-theme";
import { useFirstTimeSearch } from "../lib/hooks/census/use-first-time-search";
import { EXAMPLES } from "../lib/hooks/census/use-first-time-search";
import { BsDice3 } from "react-icons/bs";
import { FaSearch } from "react-icons/fa";
import { MapToggle } from "./geomap/map-toggle";

export const SearchBar = ({
  value = "",
  onChange,
  onEnter,
  autocompleteSuggestions = [],
}: {
  value: string;
  onChange: (text: string) => void;
  onEnter: (optionalSubmission?: string) => void;
  autocompleteSuggestions?: string[];
}) => {
  const { theme } = useTheme();
  const [isFocused, setIsFocused] = useState(false);
  const [selectedSuggestion, setSelectedSuggestion] = useState(0);
  const searchBarRef = useRef<HTMLInputElement | null>(null);

  const { placeholderExample, turnOffDemo, isFirstTimeUse } =
    useFirstTimeSearch();

  const shouldDisplay = useMemo(() => {
    return (
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
        className={clsx(
          "bg-transparent border-none w-full border-b-red-400",
          "w-full rounded-l-md rounded-r-none mx-auto shadow-md p-3",
          "pointer-events-auto",
          isFirstTimeUse && "placeholder:animate-fadeIn500"
        )}
        ref={searchBarRef}
        onFocus={() => {
          setIsFocused(true);
          turnOffDemo();
        }}
        onBlur={() => {
          setIsFocused(false);
        }}
        value={value}
        onChange={(e) => {
          onChange(e.target.value);
          setSelectedSuggestion(0);
        }}
        placeholder={
          isFirstTimeUse ? placeholderExample : "What do you want to know?"
        }
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            onEnter();
          }
          if (e.key === "ArrowDown" || e.key === "Tab") {
            const suggestionIndex =
              selectedSuggestion + 1 < autocompleteSuggestions.length
                ? selectedSuggestion + 1
                : selectedSuggestion;
            onChange(autocompleteSuggestions[suggestionIndex]);
            setSelectedSuggestion((s) => suggestionIndex);
          }
          if (e.key === "ArrowUp" || (e.key === "Tab" && e.shiftKey)) {
            const suggestionIndex =
              selectedSuggestion > 0
                ? selectedSuggestion - 1
                : selectedSuggestion;
            onChange(autocompleteSuggestions[suggestionIndex]);
            setSelectedSuggestion((s) => suggestionIndex);
          }
        }}
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
          "hover:animate-moveThroughRainbow2s focus:animate-moveThroughRainbow2s",
          "shadow-md h-12 w-12 hover:shadow-lg",
          "flex flex-row justify-center items-center space-x-2 p-2",
          "cursor-pointer",
          theme.secondaryBgColor,
          theme.secondaryFontColor
        )}
        onClick={(e) => {
          const randomIndex = Math.floor(Math.random() * EXAMPLES.length);
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
          "absolute rounded-b-md shadow-md italic border-r",
          shouldDisplay ? "block" : "hidden",
          theme.bgColor,
          theme.fontColor
        )}
        style={{
          width: searchBarRef.current?.offsetWidth,
          top: (searchBarRef.current?.offsetTop ?? 0) + 40,
        }}
      >
        {autocompleteSuggestions.map((suggestion, i) => (
          <div
            key={i}
            className={clsx(
              "p-2 cursor-pointer",
              theme.bgColor,
              theme.fontColor
            )}
            onClick={(e) => {
              onChange(suggestion);
              // @ts-ignore
              onEnter(suggestion);
            }}
          >
            {value.length > 5 &&
              suggestion.split(value).map((part, i) => (
                <>
                  {i === 0 && <span className="pointer-events-none">...</span>}
                  <span key={i} className="pointer-events-none">
                    {part}
                  </span>
                </>
              ))}
            {value.length <= 5 && (
              <span className="pointer-events-none">{suggestion}</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
