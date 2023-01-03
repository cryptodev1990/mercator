import ErrorBar from "../bars/error-bar";
import LayerCardBar from "../bars/layer-card-bar/layer-card-bar";
import GeoMap from "../geomap/geomap";
import SmallHeader from "../headers/small-header";
import TaggedSearchBar from "../bars/tagged-search-bar";
import { useState } from "react";
import CancelButton from "../buttons/cancel-button";
import SearchBar from "../bars/search-bar";
import AnalysisUIContext from "../../../src/contexts/analysis-context";
import { IntentResponse, ParsedEntity } from "src/store/search-api";
import { isServer } from "src/lib/rendering-utils";

const AnalysisView = () => {
  const [selectedIntentResponse, setSelectedIntentResponse] =
    useState<IntentResponse | null>(null);
  const [selectedEntity, setSelectedEntity] = useState<ParsedEntity | null>(
    null
  );
  const [styleDrawerOpen, setStyleDrawerOpen] = useState<boolean>(false);
  const [showTaggedSearchBar, setShowTaggedSearchBar] =
    useState<boolean>(false);

  if (isServer()) {
    return null;
  }

  return (
    <AnalysisUIContext.Provider
      value={{
        selectedIntentResponse,
        setSelectedIntentResponse,
        selectedEntity,
        setSelectedEntity,
        styleDrawerOpen,
        setStyleDrawerOpen,
        showTaggedSearchBar,
        setShowTaggedSearchBar,
      }}
    >
      <main className="flex flex-row m-auto w-full gap-1 max-w-[3000px] h-screen overflow-hidden">
        <div className="w-full flex flex-col gap-3">
          <header className="relative mt-10 select-none flex flex-row gap-4">
            <SmallHeader />
            <div className="w-full">
              {showTaggedSearchBar && (
                <div className="flex justify-around">
                  <TaggedSearchBar />
                  <CancelButton onClick={() => setShowTaggedSearchBar(false)} />
                </div>
              )}
              {!showTaggedSearchBar && <SearchBar />}
            </div>
            <ErrorBar />
          </header>
          <div className="relative h-full">
            <GeoMap />
          </div>
        </div>
        <div className="h-[100%] mt-10 bg-black-500">
          <LayerCardBar />
        </div>
      </main>
    </AnalysisUIContext.Provider>
  );
};

export default AnalysisView;
