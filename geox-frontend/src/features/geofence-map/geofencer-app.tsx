import { GeofenceMap } from "./geofence-map";
import { GeofencerSidebar } from "./shape-editor/components/geofencer-sidebar";
import { GeofencerContextContainer } from "./contexts/geofencer-context";
import Dropdown from "../../common/components/dropdown";
import { ToolButtonBank } from "./tool-button-bank/component";
import { GeofencerCommandPalette } from "./geofencer-command-palette";
import { GeofencerContextMenu } from "./geofencer-context-menu";
import { GlobalModal } from "./modals/global-modal";
import { Toaster } from "react-hot-toast";
import { UIContextContainer } from "./contexts/ui-context";
import { DbSyncContextContainer } from "./contexts/db-sync-context";
import { SelectionProvider } from "./contexts/selection/selection.context";
import { DeckContextContainer } from "./contexts/deck-context";
import { GeoShapeProvider } from "./contexts/geoshape/geoshape.context";
import { UndoProvider } from "./contexts/geoshape/undo.context";

const ContextProviderNest = ({
  contextProviders,
  children,
}: {
  contextProviders: any[];
  children: React.ReactNode;
}) => {
  for (let i = contextProviders.length - 1; i >= 0; i--) {
    const ContextProvider = contextProviders[i];
    children = <ContextProvider>{children}</ContextProvider>;
  }
  return <>{children}</>;
};

const GeofencerApp = () => {
  const ctx = [
    GeofencerContextContainer,
    DeckContextContainer,
    GeoShapeProvider,
    SelectionProvider,
    UndoProvider,
    UIContextContainer,
    DbSyncContextContainer,
  ];

  return (
    <ContextProviderNest contextProviders={ctx}>
      <GeofencerCommandPalette />
      <GeofencerContextMenu />
      <GlobalModal />
      <div className="text-white h-screen w-screen relative flex flex-col overflow-hidden">
        <div className="flex-auto w-screen relative">
          <div className="flex fixed top-0 right-0 z-10 m-2 h-0">
            <div className="z-30 mx-2 right-0 flex flex-col gap-3">
              <Dropdown />
              <ToolButtonBank />
            </div>
          </div>
          <div className="h-[95vh] px-5 py-5 flex flex-row relative">
            <GeofencerSidebar />
          </div>
          <GeofenceMap />
        </div>
        <div className="fixed bottom-0 left-0 my-7 text-gray-700 text-2xs mx-1 select-none pointer-events-none">
          Basemap tiles by
        </div>
      </div>
      <Toaster />
    </ContextProviderNest>
  );
};

export { GeofencerApp };
