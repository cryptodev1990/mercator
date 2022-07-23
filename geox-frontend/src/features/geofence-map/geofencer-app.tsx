import { GeofencerNavbar } from "./geofencer-navbar";
import { GeofenceMap } from "./geofence-map";
import { GeofenceSidebar } from "./shape-editor/geofence-sidebar";
import { useState } from "react";
import {
  Feature,
  GeoShape,
  GeoShapeCreate,
  GeoShapeUpdate,
} from "../../client";
import { MODES } from "./tool-button-bank/modes";
import { CommandPalette } from "../command-palette/component";
import { GeofencerContext, MapEditOptions } from "./context";
import buffer from "@turf/buffer";
import { ViewState } from "react-map-gl";
import { useAddShapeMutation } from "./hooks/openapi-hooks";

const GeofencerApp = () => {
  const [selectedShapes, setSelectedShapes] = useState<GeoShape[]>([]);
  const [tentativeShapes, setTentativeShapes] = useState<GeoShapeCreate[]>([]);
  const [shapeForEdit, setShapeForEdit] = useState<
    GeoShapeUpdate | null | undefined
  >();
  const [editableMode, setEditableMode] = useState<string>(MODES.ViewMode);
  const [viewport, setViewport] = useState<ViewState>({
    latitude: 37.762673511727435,
    longitude: -122.40111919656555,
    bearing: 0,
    pitch: 0,
    zoom: 11.363205994378514,
  });

  const [options, setOptions] = useState<MapEditOptions>({ denyOverlap: true });
  const { mutate: addShape } = useAddShapeMutation();

  return (
    <GeofencerContext.Provider
      value={{
        selectedShapes,
        setSelectedShapes: (shapes: GeoShape[]) => setSelectedShapes(shapes),
        tentativeShapes,
        setTentativeShapes: (shapes: GeoShapeCreate[]) =>
          setTentativeShapes(shapes),
        shapeForEdit,
        setShapeForEdit: (shape: GeoShapeUpdate | null | undefined) =>
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
        onPublish={() => {
          for (const shape of tentativeShapes) {
            addShape(shape);
          }
        }}
        onOSM={(res: Feature[]) => {
          const geoshapes = res.map((f: Feature) => {
            return { name: f.properties.name as string, geojson: f };
          });
          setTentativeShapes(geoshapes);
        }}
        onBuffer={(bufferSize: number, bufferUnits: string) => {
          const bufferedShapes = [];

          for (const shape of tentativeShapes) {
            const bufferedGeom = buffer(shape.geojson as any, bufferSize, {
              units: bufferUnits as any,
            });

            bufferedShapes.push({
              name: shape.name,
              geojson: bufferedGeom as Feature,
            });
          }

          setTentativeShapes(bufferedShapes);
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
