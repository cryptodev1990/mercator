import { useDispatch, useSelector } from "react-redux";
import { OsmSearchResponse } from "src/store/search-api";
import { selectSearchState } from "../../src/search/search-slice";
import simplur from "simplur";
import { setViewport } from "src/shapes/shape-slice";

const ZoomButton = ({ searchResult }: { searchResult: OsmSearchResponse }) => {
  const dispatch = useDispatch();
  function onClick() {
    const { results } = searchResult;
    const bbox = results?.bbox;
    if (bbox) {
      dispatch(
        setViewport({
          latitude: bbox[1],
          longitude: bbox[0],
          zoom: 12,
        })
      );
    }
  }
  return (
    <button
      className="bg-slate-200 hover:bg-slate-300 text-slate-800 font-bold py-2 px-4 rounded"
      onClick={onClick}
    >
      Zoom
    </button>
  );
};

const LayerCard = ({ searchResult }: { searchResult: OsmSearchResponse }) => {
  const { query, results } = searchResult;
  return (
    <div
      onClick={() => {
        console.log("clicked");
      }}
      className="flex flex-col w-64 h-[100px] bg-slate-100 text-slate-800 rounded-lg shadow-lg p-2 cursor-pointer"
    >
      <h4 className="font-bold text-ellipsis">{query}</h4>
      <div className="flex flex-row">
        <button className="flex-0 ml-auto">
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
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>
        <p>{simplur`${results?.features?.length} shape[|s]`}</p>
        <ZoomButton searchResult={searchResult} />
      </div>
    </div>
  );
};

const LayerCardBar = () => {
  const { searchResults } = useSelector(selectSearchState);

  return (
    <div className="flex flex-col items-center justify-start w-full h-full gap-1">
      {searchResults.map((searchResult, i) => (
        <LayerCard key={i} searchResult={searchResult} />
      ))}
    </div>
  );
};

export default LayerCardBar;
