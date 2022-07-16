import { GeofencerNavbar } from "../../features/geofence-map/geofencer-navbar";
import { GeofenceMap } from "../../features/geofence-map/geofence-map";
import { GeofenceSidebar } from "../../features/geofence-map/geofence-sidebar";
import { useState, createContext } from "react";
import { GeoShape } from "../../client";
import { EditModal } from "../edit-modal";
import { MODES } from "./tool-button-bank/modes";
import { CommandPalette } from "../command-palette/component";

interface GeofencerContextState {
  selectedShapes: GeoShape[];
  setSelectedShapes: (shapes: GeoShape[]) => void;
  shapeForEdit: GeoShape | null | undefined;
  setShapeForEdit: (shape: GeoShape | null | undefined) => void;
  editableMode: string;
  setEditableMode: (mode: string) => void;
  viewport: any;
  setViewport: (viewport: any) => void;
}

export const GeofencerContext = createContext<GeofencerContextState>({
  selectedShapes: [],
  setSelectedShapes: () => {},
  shapeForEdit: null,
  setShapeForEdit: () => {},
  editableMode: "",
  setEditableMode: () => {},
  viewport: {},
  setViewport: () => {},
});

const GeofencerView = () => {
  const [selectedShapes, setSelectedShapes] = useState<GeoShape[]>([]);
  const [shapeForEdit, setShapeForEdit] = useState<
    GeoShape | null | undefined
  >();
  const [editableMode, setEditableMode] = useState<string>(MODES.ViewMode);
  const [viewport, setViewport] = useState<any>({
    // TODO how to choose a default viewport?
    longitude: -73.986022,
    maxZoom: 20,
    latitude: 40.730743,
    zoom: 12,
  });

  return (
    <GeofencerContext.Provider
      value={{
        selectedShapes,
        setSelectedShapes: (shapes: GeoShape[]) => setSelectedShapes(shapes),
        shapeForEdit,
        setShapeForEdit: (shape: GeoShape | null | undefined) =>
          setShapeForEdit(shape),
        editableMode,
        setEditableMode: (mode: string) => setEditableMode(mode),
        viewport,
        setViewport: (viewport: any) => setViewport(viewport),
      }}
    >
      <CommandPalette
        onNominatim={(res: any) => {
          setViewport(res);
        }}
      />
      <div className="text-white h-screen relative flex flex-col">
        {shapeForEdit && <EditModal shape={shapeForEdit} />}
        <div className="h-fit w-screen p-4 bg-gradient-to-r from-slate-800 to-slate-900">
          <GeofencerNavbar />
        </div>
        <div className="flex-auto w-screen relative">
          <div className="h-[90%] px-5 py-5 flex flex-row relative">
            <GeofenceSidebar />
          </div>
          <GeofenceMap />
        </div>
      </div>
    </GeofencerContext.Provider>
  );
};

export { GeofencerView };
