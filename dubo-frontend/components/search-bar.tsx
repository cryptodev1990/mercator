import clsx from "clsx";
import { useMemo, useState } from "react";

export const SearchBar = ({
  value = "",
  onChange,
  onEnter,
  autocompleteSuggestions = [],
}: {
  value: string;
  onChange: (text: string) => void;
  onEnter: (e: React.KeyboardEvent<HTMLInputElement>) => void;
  autocompleteSuggestions?: string[];
}) => {
  const [isFocused, setIsFocused] = useState(false);
  const [selectedSuggestion, setSelectedSuggestion] = useState(0);
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
    <div
      className={clsx(
        "absolute top-[10%] z-50 mx-auto w-full",
        "bg-slate-100 rounded-md shadowkmd text-slate-900 p-3",
        "hover:bg-slate-200 "
      )}
    >
      <input
        className="bg-transparent border-none w-full border-b-red-400"
        onFocus={() => setIsFocused(true)}
        // onBlur={() => setIsFocused(false)}
        value={value}
        onChange={(e) => {
          onChange(e.target.value);
          setSelectedSuggestion(0);
        }}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            onEnter(e);
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
      {/* autocomplete suggestions */}
      <div
        className={clsx(
          "absolute bg-slate-100 w-full rounded-b-md shadow-md",
          shouldDisplay ? "block" : "hidden"
        )}
      >
        {autocompleteSuggestions.map((suggestion, i) => (
          <div
            key={i}
            className="p-2 hover:bg-slate-200 cursor-pointer"
            onClick={(e) => {
              onChange(suggestion);
              // @ts-ignore
              onEnter(e);
            }}
          >
            {value.length > 5 &&
              suggestion.split(value).map((part, i) => (
                <>
                  {i === 0 && (
                    <span className="text-slate-900 pointer-events-none">
                      ...
                    </span>
                  )}
                  <span key={i} className="text-slate-900 pointer-events-none">
                    {part}
                  </span>
                </>
              ))}
            {value.length <= 5 && (
              <span className="text-slate-900 pointer-events-none">
                {suggestion}
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
