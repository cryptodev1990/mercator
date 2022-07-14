import { GeofencerNavbar } from "../../features/geofence-map/geofencer-navbar";
import { GeofenceMap } from "../../features/geofence-map/geofence-map";
import { GeofenceSidebar } from "../../features/geofence-map/geofence-sidebar";
import { useState, createContext } from "react";
import { GeoShape } from "../../client";
import { EditModal } from "../edit-modal";

interface GeofencerContextState {
  selectedShapes: GeoShape[];
  setSelectedShapes: (shapes: GeoShape[]) => void;
  shapeForEdit: GeoShape | null | undefined;
  setShapeForEdit: (shape: GeoShape | null | undefined) => void;
}

export const GeofencerContext = createContext<GeofencerContextState>({
  selectedShapes: [],
  setSelectedShapes: () => {},
  shapeForEdit: null,
  setShapeForEdit: () => {},
});

const GeofencerView = () => {
  const [selectedShapes, setSelectedShapes] = useState<GeoShape[]>([]);
  const [shapeForEdit, setShapeForEdit] = useState<
    GeoShape | null | undefined
  >();

  return (
    <GeofencerContext.Provider
      value={{
        selectedShapes,
        setSelectedShapes: (shapes: GeoShape[]) => setSelectedShapes(shapes),
        shapeForEdit,
        setShapeForEdit: (shape: GeoShape | null | undefined) =>
          setShapeForEdit(shape),
      }}
    >
      <div className="text-white">
        {shapeForEdit && <EditModal shape={shapeForEdit} />}
        <div className="h-fit w-screen p-4 bg-gradient-to-r from-slate-800 to-slate-900">
          <GeofencerNavbar />
        </div>
        <div className="h-screen w-screen relative">
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
