import { GeofenceMap } from "./shape-map";
import { GeofencerSidebar } from "./sidebar";
import { GeofencerContextContainer } from "../contexts/geofencer-context";
import Dropdown from "../../../common/components/dropdown";
import { ToolButtonBank } from "./tool-button-bank/tool-button-bank";
import { CommandPalette } from "./command-palette";
import { RightClickMenu } from "./right-click-menu";
import { GlobalModal } from "./modals";
import { Toaster } from "react-hot-toast";
import { UIContextContainer } from "../contexts/ui-context";
import { DbSyncContextContainer } from "../contexts/db-sync-context";
import { SelectionContextProvider } from "../contexts/selection/selection.context";
import { DeckContextProvider } from "../contexts/deck-context";
import { GeoShapeWriteContextProvider } from "../contexts/geoshape-write/context";
import { GeoShapeMetadataProvider } from "../contexts/geoshape-metadata/context";
import { Tooltip } from "../../../common/components/tooltip";
import { DocsButton, DocsIframe } from "./docs-iframe";

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
    DeckContextProvider,
    GeofencerContextContainer,
    GeoShapeMetadataProvider,
    // GeoShapeWriteContextProvider needs to be after the deck and selection contexts
    GeoShapeWriteContextProvider,
    SelectionContextProvider,
    UIContextContainer,
    DbSyncContextContainer,
  ];

  return (
    <ContextProviderNest contextProviders={ctx}>
      <CommandPalette />
      <RightClickMenu />
      <GlobalModal />
      <div className="text-white h-screen w-screen relative flex flex-col overflow-hidden border ">
        <div className="flex-auto w-screen relative border m-0 p-0">
          <div className="flex fixed top-0 right-0 z-10 m-2 h-0">
            <div className="z-10 mx-2 flex flex-col h-screen space-y-3 items-center">
              <Dropdown />
              <ToolButtonBank />
              <DocsButton />
            </div>
            <DocsIframe />
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
      <Tooltip />
    </ContextProviderNest>
  );
};

export { GeofencerApp };
