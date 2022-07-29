import { createContext, ReactNode, useState } from "react";
import { ViewState } from "react-map-gl";
import { GeoShape, GeoShapeCreate } from "../../client";
import { EditorMode } from "./cursor-modes";
import { GlobalEditorOptions } from "./types";

interface GeofencerContextState {
  shapes: GeoShape[];
  setShapes:
    | ((shapes: GeoShape[]) => void)
    | ((prevShapes: GeoShape[]) => GeoShape[]);
  viewport: any;
  setViewport: (viewport: any) => void;
  options: GlobalEditorOptions;
  setOptions: (options: GlobalEditorOptions) => void;
  selectedShapeUuids: Record<string, boolean>;
  setSelectedShapeUuids: (selectedShapes: Record<string, boolean>) => void;
  shapeForMetadataEdit: GeoShape | null;
  setShapeForMetadataEdit: (shape: GeoShape | null) => void;
  tentativeShapes: GeoShapeCreate[];
  setTentativeShapes: (shapes: GeoShapeCreate[]) => void;
}

export const GeofencerContext = createContext<GeofencerContextState>({
  shapes: [],
  setShapes: () => {},
  options: {
    denyOverlap: true,
    cursorMode: EditorMode.ViewMode,
  },
  setOptions: (newState: GlobalEditorOptions) => {},
  viewport: {},
  setViewport: () => {},
  selectedShapeUuids: {},
  setSelectedShapeUuids: () => {},
  shapeForMetadataEdit: null,
  setShapeForMetadataEdit: () => {},
  tentativeShapes: [],
  setTentativeShapes: () => {},
});
GeofencerContext.displayName = "GeofencerContext";

export const GeofencerContextContainer = ({
  children,
}: {
  children: ReactNode[];
}) => {
  const [shapes, setShapes] = useState<GeoShape[]>([]);
  const [viewport, setViewport] = useState<ViewState>({
    latitude: 37.762673511727435,
    longitude: -122.40111919656555,
    bearing: 0,
    pitch: 0,
    zoom: 11.363205994378514,
  });

  const [options, setOptions] = useState<GlobalEditorOptions>({
    denyOverlap: true,
    cursorMode: EditorMode.ViewMode,
  });

  const [selectedShapeUuids, setSelectedShapeUuids] = useState<
    Record<string, boolean>
  >({});

  const [shapeForMetadataEdit, setShapeForMetadataEdit] =
    useState<GeoShape | null>(null);

  const [tentativeShapes, setTentativeShapes] = useState<GeoShapeCreate[]>([]);

  return (
    <GeofencerContext.Provider
      value={{
        shapes,
        setShapes: (shapes: GeoShape[]) => setShapes(shapes),
        viewport,
        setViewport: (viewport: any) => setViewport(viewport),
        options,
        setOptions: (options: GlobalEditorOptions) => setOptions(options),
        selectedShapeUuids,
        setSelectedShapeUuids: (selectedShapes: Record<string, boolean>) =>
          setSelectedShapeUuids(selectedShapes),
        shapeForMetadataEdit,
        setShapeForMetadataEdit: (shape: GeoShape | null) =>
          setShapeForMetadataEdit(shape),
        tentativeShapes,
        setTentativeShapes: (tentativeShapes: GeoShapeCreate[]) =>
          setTentativeShapes(tentativeShapes),
      }}
    >
      {children}
    </GeofencerContext.Provider>
  );
};
