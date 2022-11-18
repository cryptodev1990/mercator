import Fuse from "fuse.js";
import { useContext, useEffect, useMemo, useRef, useState } from "react";
import {
  ParticleCandidate,
  SearchContext,
} from "../../features/search/context";

const CompletionMenu = ({
  candidates,
  onSelect,
}: {
  candidates: ParticleCandidate[];
  onSelect: (candidateIndex: number) => void;
}) => {
  const { searchText, setSearchText } = useContext(SearchContext);

  const [hits, setHits] = useState<Fuse.FuseResult<ParticleCandidate>[]>([]);
  const fuseEngine = useRef<Fuse<ParticleCandidate>>(null);

  useEffect(() => {
    // @ts-ignore
    fuseEngine.current = new Fuse(candidates, {
      keys: ["name"],
    });
    setHits([]);
  }, [candidates]);

  useEffect(() => {
    if (!fuseEngine || !fuseEngine.current) {
      console.warn("No fuse");
      return;
    }
    // @ts-ignore
    try {
      const results = fuseEngine?.current?.search(searchText);
      if (results.length > 0) {
        setHits(results);
      }
    } catch (e) {
      console.error(e);
    }
  }, [searchText]);

  if (!candidates || candidates.length === 0) {
    console.warn("No candidates");
    return null;
  }

  return (
    <div className="w-full px-4">
      <div className="">
        {hits[0] && (
          <div
            className="p-2 cursor-pointer"
            tabIndex={0}
            key={hits[0].item.name + "1a"}
            onClick={() => onSelect(hits[0].refIndex)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                onSelect(hits[0].refIndex ?? 0);
              }
            }}
          >
            {hits[0].item.name}
          </div>
        )}
        {candidates.map((part, i) => {
          return (
            <>
              <div
                className="text-gray-400 text-sm"
                style={{
                  color: hits.find((x) => x.refIndex === i) ? "white" : "gray",
                }}
                key={part.name + "" + i}
                tabIndex={i + 1}
                onClick={() => onSelect(i)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    onSelect(i);
                  }
                }}
              >
                <p>{part.name}</p>
              </div>
            </>
          );
        })}
      </div>
    </div>
  );
};

const CancelButton = () => {
  const { clearQuery } = useContext(SearchContext);
  return (
    <div
      className="cursor-pointer"
      onClick={() => {
        clearQuery();
      }}
    >
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

const QueryPreview = () => {
  const { searchText, queryPreview } = useContext(SearchContext);

  return (
    <div className="w-full px-4 flex flex-row">
      <CancelButton />
      <p>{queryPreview || searchText}</p>
    </div>
  );
};

export const SearchBar = () => {
  const focusRef = useRef<HTMLInputElement>(null);

  const {
    searchText,
    setSearchText,
    candidates,
    setPhaseResult,
    queryPreview,
  } = useContext(SearchContext);

  useEffect(() => {
    if (focusRef.current) {
      focusRef.current.focus();
    }
  }, []);

  useEffect(() => {
    if (searchText === "" && focusRef.current) {
      focusRef.current.focus();
    }
  }, [searchText]);

  const activeSearch = searchText || queryPreview;

  return (
    <div className="flex flex-col justify-start items-center w-[80vw] m-auto space-y-10">
      <input
        ref={focusRef}
        value={searchText}
        className="border border-slate-200 rounded h-12 px-4 z-10 w-full"
        placeholder="Start typing to search..."
        onChange={(e) => setSearchText(e.target.value)}
      />
      {activeSearch && <QueryPreview />}
      {activeSearch && (
        <CompletionMenu
          candidates={candidates}
          onSelect={(candidateIndex: number) => setPhaseResult(candidateIndex)}
        />
      )}
    </div>
  );
};
