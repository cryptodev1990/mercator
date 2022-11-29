import { useSelector } from "react-redux";
import { OsmSearchResponse } from "src/store/search-api";
import { selectSearchState } from "../../src/search/search-slice";
import simplur from "simplur";

const LayerCard = ({ searchResult }: { searchResult: OsmSearchResponse }) => {
  const { query, results } = searchResult;
  return (
    <div className="flex flex-col w-64 h-full bg-white text-slate-800 rounded-lg shadow-lg">
      <h4>{query}</h4>
      <p>{simplur`${results?.features?.length} shape[|s]`}</p>
    </div>
  );
};

const LayerCardBar = () => {
  const { searchResults } = useSelector(selectSearchState);

  return (
    <div className="flex flex-row items-center bg-white justify-center w-full h-full z-10">
      {searchResults.map((searchResult, i) => (
        <LayerCard key={i} searchResult={searchResult} />
      ))}
    </div>
  );
};

export default LayerCardBar;
