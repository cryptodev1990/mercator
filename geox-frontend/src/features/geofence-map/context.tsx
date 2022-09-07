import { createContext, ReactNode, useEffect, useRef, useState } from "react";
import { ViewState } from "react-map-gl";
import { Feature, GeoShape, GeoShapeCreate } from "../../client";
// @ts-ignore
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
  uploadedGeojson: Feature[];
  setUploadedGeojson: (geojson: Feature[]) => void;
  virtuosoRef: any;
  mapRef: any;
  guideShapes: GeoShapeCreate[];
  setGuideShapes: (shapes: GeoShapeCreate[]) => void;
  selectedFeatureIndexes: number[];
  setSelectedFeatureIndexes: (indexes: number[]) => void;
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
  uploadedGeojson: [],
  setUploadedGeojson: () => {},
  virtuosoRef: null,
  mapRef: null,
  guideShapes: [],
  setGuideShapes: () => {},
  selectedFeatureIndexes: [],
  setSelectedFeatureIndexes: () => {},
});
GeofencerContext.displayName = "GeofencerContext";

export const GeofencerContextContainer = ({
  children,
}: {
  children: ReactNode[];
}) => {
  const [shapes, setShapes] = useState<GeoShape[]>([]);
  const storedViewport = localStorage.getItem("viewport");
  const [viewport, setViewport] = useState<ViewState>(
    storedViewport
      ? JSON.parse(storedViewport)
      : {
          latitude: 37.762673511727435,
          longitude: -122.40111919656555,
          bearing: 0,
          pitch: 0,
          zoom: 11.363205994378514,
        }
  );

  useEffect(() => {
    // Store viewport in local storage
    localStorage.setItem(
      "viewport",
      JSON.stringify({
        latitude: viewport.latitude,
        longitude: viewport.longitude,
        zoom: viewport.zoom,
      })
    );
  }, [viewport]);

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
  const [guideShapes, setGuideShapes] = useState<GeoShapeCreate[]>([]);

  const [uploadedGeojson, setUploadedGeojson] = useState<Feature[]>([]);
  const virtuosoRef = useRef(null);
  const mapRef = useRef(null);

  const [selectedFeatureIndexes, setSelectedFeatureIndexes] = useState<
    number[]
  >([]);

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
        uploadedGeojson,
        setUploadedGeojson: (geojson: Feature[]) => setUploadedGeojson(geojson),
        virtuosoRef,
        mapRef,
        guideShapes,
        setGuideShapes: (shapes: GeoShapeCreate[]) => setGuideShapes(shapes),
        selectedFeatureIndexes,
        setSelectedFeatureIndexes: (indexes: number[]) =>
          setSelectedFeatureIndexes(indexes),
      }}
    >
      {children}
    </GeofencerContext.Provider>
  );
};
