import { useSelector } from "react-redux";
import { selectSearchState } from "../../../../src/search/search-slice";
import { selectGeoMapState } from "src/shapes/shape-slice";
import LayerCard from "./layer-card";
import { useContext, useEffect } from "react";
import AnalysisUIContext from "../../../../src/contexts/analysis-context";

const LayerCardBar = () => {
  const { searchResults } = useSelector(selectSearchState);
  const { layerStyles } = useSelector(selectGeoMapState);
  const ctx = useContext(AnalysisUIContext);

  useEffect(() => {
    console.log(ctx);
  }, [ctx]);

  if (!searchResults) {
    return null;
  }

  return (
    <div className="flex flex-col items-center justify-start w-full h-[90vh] gap-1 overflow-y-scroll">
      <LayerCard
        searchResult={searchResults[0]}
        layerStyle={layerStyles[0]}
        onClick={() => ctx.setSelectedIntentResponse(searchResults[0])}
      />
      {searchResults.map((searchResult, i) => {
        return (
          <>
            {ctx.selectedIntentResponse?.id === searchResult.id ? (
              <div className="w-full h-1 bg-red-500" />
            ) : null}
            <LayerCard
              key={searchResult.id}
              searchResult={searchResult}
              layerStyle={layerStyles[i]}
              onClick={() => {
                ctx.setSelectedIntentResponse(searchResult);
                ctx.setShowTaggedSearchBar(true);
              }}
            />
          </>
        );
      })}
    </div>
  );
};

export default LayerCardBar;
