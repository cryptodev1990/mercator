import { createContext, useEffect, useMemo, useState } from "react";

type SearchContextType = {
  searchText: string;
  setSearchText: (text: string) => void;
  candidates: ParticleCandidate[];
  setPhaseResult: (candidateIndex: number) => void;
  queryPreview: string | null;
  clearQuery: () => void;
};

type Intent = {
  name: string;
  description: string;
  numPhases: number;
  slots: string[];
};

export const SearchContext = createContext<SearchContextType>({
  searchText: "",
  setSearchText: () => {},
  candidates: [],
  setPhaseResult: () => {},
  queryPreview: null,
  clearQuery: () => {},
});

export type ParticleCandidate = {
  name: string;
};

const NOUN_CLASS_LIST = [
  { name: "schools" },
  { name: "libraries" },
  { name: "zoos" },
  { name: "italian delis" },
  { name: "boutique hotels" },
  { name: "hotels" },
  { name: "banks" },
  { name: "restaurants" },
  { name: "coffee shops" },
  { name: "museums" },
  { name: "parks" },
  { name: "bars" },
  { name: "galleries" },
  { name: "stores" },
  { name: "shops" },
  { name: "cafes" },
  { name: "theaters" },
  { name: "gyms" },
  { name: "hospitals" },
  { name: "pharmacies" },
  { name: "clinics" },
  { name: "dentists" },
  { name: "doctors" },
  { name: "optometrists" },
  { name: "chiropractors" },
  { name: "hair salons" },
  { name: "nail salons" },
  { name: "massage therapists" },
  { name: "plumbers" },
  { name: "electricians" },
  { name: "car mechanics" },
  { name: "pet hospitals" },
  { name: "car dealerships" },
  { name: "car washes" },
  { name: "gas stations" },
  { name: "pet stores" },
  { name: "italian restaurants" },
  { name: "mexican restaurants" },
  { name: "chinese restaurants" },
  { name: "japanese restaurants" },
  { name: "thai restaurants" },
  { name: "yoga studios" },
  { name: "golf courses" },
  { name: "bowling alleys" },
  { name: "movie theaters" },
  { name: "concert halls" },
];

const PREPOSITION_LIST = [
  { name: "near" },
  { name: "in" },
  { name: "at" },
  { name: "around" },
  { name: "close to" },
  { name: "close by" },
  { name: "close" },
  { name: "nearby" },
];

type Node = {
  name: string;
  children: Node[];
};

type NounClassNode = {
  name: string;
  children: NounClassNode[];
  prepositions: string[];
};

type PrepositionNode = {
  name: string;
  children: NounClassNode[];
};

type ConjunctionNode = {
  name: string;
  children: PrepositionNode[];
};

const SearchContextProvider = ({ children }: { children: React.ReactNode }) => {
  const [searchText, setSearchText] = useState("");
  const [phase, setPhase] = useState(0);
  const [result, setResult] = useState<ParticleCandidate[]>([]);
  const [intent, setIntent] = useState<Intent>({
    name: "find",
    description: "Find a place",
    numPhases: 3,
    slots: ["noun_class", "preposition", "noun_class"],
  });

  useEffect(() => {
    setPhase(0);
  }, [intent]);

  useEffect(() => {
    if (phase + 1 === intent.numPhases) {
      console.log("RUN QUERY CALL HERE");
    }
  }, [phase]);

  useEffect(() => {
    console.log(result);
  }, [result]);

  const getCandidates = useMemo(
    () => (): ParticleCandidate[] => {
      return [NOUN_CLASS_LIST, PREPOSITION_LIST, NOUN_CLASS_LIST][phase];
    },
    [phase]
  );

  const candidates = getCandidates();

  function clearQuery() {
    setResult([]);
    setPhase(0);
    setSearchText("");
  }

  const setPhaseResult = useMemo(
    () => (resultIdx: number) => {
      const candidates = getCandidates();
      const copy = [...result];
      copy[phase] = candidates[resultIdx];
      setResult(copy);
      setPhase(phase + 1);
      setSearchText("");
    },
    [phase]
  );

  const queryPreview = useMemo(() => {
    return result
      .map((r) => r.name)
      .join(" ")
      .trim();
  }, [result]);

  return (
    <SearchContext.Provider
      value={{
        searchText,
        setSearchText,
        candidates,
        setPhaseResult,
        queryPreview,
        clearQuery,
      }}
    >
      {children}
    </SearchContext.Provider>
  );
};

export default SearchContextProvider;
