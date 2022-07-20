import { GeofencerNavbar } from "./geofencer-navbar";
import { GeofenceMap } from "./geofence-map";
import { GeofenceSidebar } from "./geofence-sidebar";
import { useState } from "react";
import { GeoShape, GeoShapeCreate } from "../../client";
import { MODES } from "./tool-button-bank/modes";
import { CommandPalette } from "../command-palette/component";
import { GeofencerContext, MapEditOptions } from "./context";
import { ViewState } from "react-map-gl";

const GeofencerApp = () => {
  const [selectedShapes, setSelectedShapes] = useState<GeoShape[]>([]);
  const [shapeForEdit, setShapeForEdit] = useState<
    GeoShapeCreate | null | undefined
  >();
  // TODO change back
  const [editableMode, setEditableMode] = useState<string>(MODES.LassoDrawMode);
  // TODO change back
  // const [editableMode, setEditableMode] = useState<string>(MODES.ViewMode);
  const [viewport, setViewport] = useState<ViewState>({
    latitude: 37.762673511727435,
    longitude: -122.40111919656555,
    bearing: 0,
    pitch: 0,
    zoom: 11.363205994378514,
  });

  const [options, setOptions] = useState<MapEditOptions>({ denyOverlap: true });

  return (
    <GeofencerContext.Provider
      value={{
        selectedShapes,
        setSelectedShapes: (shapes: GeoShape[]) => setSelectedShapes(shapes),
        shapeForEdit,
        setShapeForEdit: (shape: GeoShapeCreate | null | undefined) =>
          setShapeForEdit(shape),
        editableMode,
        setEditableMode: (mode: string) => setEditableMode(mode),
        viewport,
        setViewport: (viewport: any) => setViewport(viewport),
        options,
        setOptions: (options: MapEditOptions) => setOptions(options),
      }}
    >
      <CommandPalette
        onNominatim={(res: any) => {
          setViewport(res);
        }}
      />
      <div className="text-white h-screen relative flex flex-col">
        <div className="h-fit min-w-[400px] p-5 bg-gradient-to-r from-slate-800 to-slate-900">
          <GeofencerNavbar />
        </div>
        <div className="flex-auto w-screen relative">
          <div className="h-[85vh] px-5 py-5 flex flex-row relative">
            <GeofenceSidebar />
          </div>
          <GeofenceMap />
        </div>
      </div>
    </GeofencerContext.Provider>
  );
};

export { GeofencerApp };
