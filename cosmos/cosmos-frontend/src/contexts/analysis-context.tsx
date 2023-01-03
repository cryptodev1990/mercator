import { createContext } from "react";
import { IntentResponse, ParsedEntity } from "src/store/search-api";

export type AnalysisUIContextType = {
  selectedIntentResponse: IntentResponse | null;
  setSelectedIntentResponse: (ir: IntentResponse | null) => void;
  selectedEntity: ParsedEntity | null;
  setSelectedEntity: (entity: ParsedEntity | null) => void;
  styleDrawerOpen: boolean;
  setStyleDrawerOpen: (open: boolean) => void;
  showTaggedSearchBar: boolean;
  setShowTaggedSearchBar: (show: boolean) => void;
};

const AnalysisUIContext = createContext<AnalysisUIContextType>({
  selectedIntentResponse: null,
  setSelectedIntentResponse: () => {},
  selectedEntity: null,
  setSelectedEntity: () => {},
  styleDrawerOpen: false,
  setStyleDrawerOpen: () => {},
  showTaggedSearchBar: false,
  setShowTaggedSearchBar: () => {},
});

export default AnalysisUIContext;
