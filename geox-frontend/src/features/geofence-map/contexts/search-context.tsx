import { createContext, useState } from "react";

interface SearchContextI {
  searchResults: Set<string> | null;
  setSearchResults: (results: string[] | null) => void;
}

export const SearchContext = createContext<SearchContextI>({
  searchResults: null,
  setSearchResults: () => {},
});
SearchContext.displayName = "SearchContext";

export const SearchContextProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const [searchResults, setSearchResults] = useState<Set<string> | null>(null);

  return (
    <SearchContext.Provider
      value={{
        searchResults,
        setSearchResults: (results) => {
          if (results) {
            setSearchResults(new Set(results));
          } else {
            setSearchResults(null);
          }
        },
      }}
    >
      {children}
    </SearchContext.Provider>
  );
};
