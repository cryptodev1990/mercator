import { GeofenceMap } from "./geofence-map";
import { GeofenceSidebar } from "./shape-editor/components/geofence-sidebar";
import { GeofencerContextContainer } from "./context";
import { NamespaceListBox } from "./namespace-list-box";
import Dropdown from "../../common/components/dropdown";
import { ToolButtonBank } from "./tool-button-bank/component";
import { GeofencerCommandPalette } from "./geofencer-command-palette";

const GeofencerApp = () => {
  return (
    <GeofencerContextContainer>
      <GeofencerCommandPalette />
      <div className="text-white h-screen relative flex flex-col">
        <div className="flex-auto w-screen relative">
          <div className="flex fixed top-0 right-0 z-10 m-2 h-0">
            <NamespaceListBox />
            <div className="z-30 mx-2 right-0 flex flex-col gap-3">
              <Dropdown />
              <ToolButtonBank />
            </div>
          </div>
          <div className="h-[95vh] px-5 py-5 flex flex-row relative">
            <GeofenceSidebar />
          </div>
          <GeofenceMap />
        </div>
        <div className="fixed bottom-0 left-0 my-7 text-gray-700 text-2xs mx-1 select-none pointer-events-none">
          Basemap tiles by
        </div>
      </div>
    </GeofencerContextContainer>
  );
};

export { GeofencerApp };
