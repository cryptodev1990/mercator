import { createContext, useEffect, useRef, useState } from "react";
import { ViewState } from "react-map-gl";
import { Feature, GeoShapeCreate } from "../../../client";
import { GeoShapeMetadata } from "../../../client/models/GeoShapeMetadata";
import { EditorMode } from "../cursor-modes";
import {
  useGetAllShapesMetadata,
  useNumShapesQuery,
} from "../hooks/openapi-hooks";
import { GlobalEditorOptions } from "../types";

interface GeofencerContextState {
  shapeMetadata: GeoShapeMetadata[];
  setShapeMetadata: (metadata: GeoShapeMetadata[]) => void;
  shapeMetadataIsLoading: boolean;
  viewport: any;
  setViewport: (viewport: any) => void;
  options: GlobalEditorOptions;
  setOptions: (options: GlobalEditorOptions) => void;
  shapeForPropertyEdit: GeoShapeMetadata | null;
  setShapeForPropertyEdit: (shape: GeoShapeMetadata | null) => void;
  tentativeShapes: GeoShapeCreate[];
  setTentativeShapes: (shapes: GeoShapeCreate[]) => void;
  uploadedGeojson: Feature[];
  setUploadedGeojson: (geojson: Feature[]) => void;
  virtuosoRef: any;
  mapRef: any;
  selectedFeatureIndexes: number[];
  setSelectedFeatureIndexes: (indexes: number[]) => void;
  numShapes: number;
  numShapesIsLoading: boolean;
}

export const GeofencerContext = createContext<GeofencerContextState>({
  shapeMetadata: [],
  setShapeMetadata: () => {},
  shapeMetadataIsLoading: false,
  options: {
    denyOverlap: true,
    cursorMode: EditorMode.ViewMode,
  },
  setOptions: (newState: GlobalEditorOptions) => {},
  viewport: {},
  setViewport: () => {},
  shapeForPropertyEdit: null,
  setShapeForPropertyEdit: () => {},
  tentativeShapes: [],
  setTentativeShapes: () => {},
  uploadedGeojson: [],
  setUploadedGeojson: () => {},
  virtuosoRef: null,
  mapRef: null,
  selectedFeatureIndexes: [],
  setSelectedFeatureIndexes: () => {},
  numShapes: 0,
  numShapesIsLoading: false,
});
GeofencerContext.displayName = "GeofencerContext";

export const GeofencerContextContainer = ({ children }: { children: any }) => {
  const [shapeMetadata, setShapeMetadata] = useState<GeoShapeMetadata[]>([]);
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

  const { data: numShapesPayload, isLoading: numShapesIsLoading } =
    useNumShapesQuery();

  const { data: remoteShapeMetadata, isLoading: shapeMetadataIsLoading } =
    useGetAllShapesMetadata();

  useEffect(() => {
    if (remoteShapeMetadata === undefined) {
      return;
    }
    setShapeMetadata(remoteShapeMetadata);
  }, [remoteShapeMetadata]);

  useEffect(() => {
    // Store viewport in local storage
    if (
      !Number.isFinite(viewport.latitude) ||
      !Number.isFinite(viewport.longitude) ||
      !Number.isFinite(viewport.zoom)
    ) {
      return;
    }
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

  useEffect(() => {
    // If no mode is assigned, set to edit mode
    if (!options.cursorMode) {
      setOptions({ ...options, cursorMode: EditorMode.EditMode });
    }
  }, [options, options.cursorMode]);

  const [shapeForPropertyEdit, setShapeForPropertyEdit] =
    useState<GeoShapeMetadata | null>(null);

  const [tentativeShapes, setTentativeShapes] = useState<GeoShapeCreate[]>([]);

  const [uploadedGeojson, setUploadedGeojson] = useState<Feature[]>([]);
  const virtuosoRef = useRef(null);
  const mapRef = useRef(null);

  const [selectedFeatureIndexes, setSelectedFeatureIndexes] = useState<
    number[]
  >([]);

  return (
    <GeofencerContext.Provider
      value={{
        shapeMetadata,
        shapeMetadataIsLoading,
        setShapeMetadata: (shapes: GeoShapeMetadata[]) =>
          setShapeMetadata(shapes),
        viewport,
        setViewport: (viewport: any) => setViewport(viewport),
        options,
        setOptions: (options: GlobalEditorOptions) => setOptions(options),
        shapeForPropertyEdit,
        setShapeForPropertyEdit: (shape: GeoShapeMetadata | null) =>
          setShapeForPropertyEdit(shape),
        tentativeShapes,
        setTentativeShapes: (tentativeShapes: GeoShapeCreate[]) =>
          setTentativeShapes(tentativeShapes),
        uploadedGeojson,
        setUploadedGeojson: (geojson: Feature[]) => setUploadedGeojson(geojson),
        virtuosoRef,
        mapRef,
        numShapes: numShapesPayload?.num_shapes || 0,
        numShapesIsLoading,
        selectedFeatureIndexes,
        setSelectedFeatureIndexes: (indexes: number[]) =>
          setSelectedFeatureIndexes(indexes),
      }}
    >
      {children}
    </GeofencerContext.Provider>
  );
};
