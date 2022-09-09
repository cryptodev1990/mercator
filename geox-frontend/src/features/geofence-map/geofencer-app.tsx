import { GeofenceMap } from "./geofence-map";
import { GeofenceSidebar } from "./shape-editor/components/geofence-sidebar";
// @ts-ignore
import { GeofencerContextContainer } from "./context";
import { NamespaceListBox } from "./namespace-list-box";
import Dropdown from "../../common/components/dropdown";
import { ToolButtonBank } from "./tool-button-bank/component";
import { GeofencerCommandPalette } from "./geofencer-command-palette";
import { GeofencerContextMenu } from "./geofencer-context-menu";
import { UploadModal } from "./upload-modal";
import { Toaster } from "react-hot-toast";
import { useEffect, useState } from "react";

const GeofencerApp = () => {
  const [uploadModalOpen, setUploadModalOpen] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setUploadModalOpen(() => false);
      }
      if (e.ctrlKey && e.key === "u") {
        setUploadModalOpen((prevState) => !prevState);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  return (
    <GeofencerContextContainer>
      <GeofencerCommandPalette />
      <GeofencerContextMenu />
      <UploadModal open={uploadModalOpen} setOpen={setUploadModalOpen} />
      <div className="text-white h-screen w-screen relative flex flex-col overflow-hidden">
        <div className="flex-auto w-screen relative">
          <div className="flex fixed top-0 right-0 z-10 m-2 h-0">
            <NamespaceListBox />
            <div className="z-30 mx-2 right-0 flex flex-col gap-3">
              <Dropdown />
              <ToolButtonBank />
            </div>
          </div>
          <div className="h-[95vh] px-5 py-5 flex flex-row relative">
            <GeofenceSidebar setUploadModalOpen={setUploadModalOpen} />
          </div>
          <GeofenceMap />
        </div>
        <div className="fixed bottom-0 left-0 my-7 text-gray-700 text-2xs mx-1 select-none pointer-events-none">
          Basemap tiles by
        </div>
      </div>
      <Toaster />
    </GeofencerContextContainer>
  );
};

export { GeofencerApp };
