import { createContext, useReducer } from "react";
import { UseMutateFunction } from "react-query";
import {
  GeoShape,
  GeoShapeCreate,
  GeoShapeMetadata,
  GeoShapeUpdate,
  ShapeCountResponse,
} from "../../../../client";
import { aggressiveLog } from "../../../../common/aggressive-log";
import { useApi } from "./api.hook";
import { geoshapeReducer, initialState, State } from "./geoshape.reducer";

export interface GeoShapeContextI {
  // API call - get all shape metadata (shape minus geometry)
  shapeMetadata: GeoShapeMetadata[];
  shapeMetadataIsLoading: boolean;
  shapeMetadataError: Error | null;
  // API call - num shapes
  numShapes: number | null;
  numShapesIsLoading: boolean;
  numShapesError: Error | null;
  // Refreshes the shape tiles
  tileCacheKey: number;
  // API call - bulk delete
  deleteShapes: UseMutateFunction<
    ShapeCountResponse,
    unknown,
    string[],
    unknown
  >;
  // API call - update shape
  updateShape: UseMutateFunction<
    GeoShapeMetadata,
    unknown,
    GeoShapeUpdate,
    unknown
  >;
  // API call - add shape
  addShape: UseMutateFunction<
    GeoShapeMetadata,
    unknown,
    GeoShapeCreate,
    unknown
  >;
  // API call - bulk add shape
  bulkAddShapes: UseMutateFunction<
    ShapeCountResponse,
    unknown,
    GeoShapeCreate[],
    unknown
  >;
  bulkAddFromSplit: UseMutateFunction<
    ShapeCountResponse,
    unknown,
    GeoShapeCreate[],
    unknown
  >;
  addShapeAndEdit: any;
  updateLoading: boolean;
  updatedShapeIds: string[];
}

export const GeoShapeContext = createContext<GeoShapeContextI>({
  shapeMetadata: [],
  shapeMetadataIsLoading: false,
  shapeMetadataError: null,
  numShapes: null,
  numShapesIsLoading: false,
  numShapesError: null,
  tileCacheKey: 0,
  deleteShapes: async () => {},
  updateShape: async () => {},
  addShape: async () => {},
  bulkAddShapes: async () => {},
  bulkAddFromSplit: async () => {},
  updateLoading: false,
  addShapeAndEdit: async () => {},
  updatedShapeIds: [],
});

GeoShapeContext.displayName = "GeoShapeContext";

export const GeoShapeProvider = ({ children }: { children: any }) => {
  const [state, dispatch]: [State, any] = useReducer(
    aggressiveLog(geoshapeReducer),
    initialState
  );
  const api = useApi(dispatch);

  function opLog(op: string, payload: any) {
    dispatch({
      type: "OP_LOG_ADD",
      op,
      payload,
    });
  }

  function bulkAddShapes(shapes: GeoShapeCreate[], ...args: any[]) {
    opLog("BULK_ADD_SHAPES", shapes);
    return api.bulkAddShapesApi(shapes, ...args);
  }

  function bulkAddFromSplit(
    shapes: GeoShapeCreate[],
    { onSuccess, onError }: any
  ) {
    opLog("BULK_ADD_SHAPE_SPLIT", shapes);
    return api.bulkAddShapesApi(shapes, {
      onSuccess,
      onError,
    });
  }

  function addShape(shape: GeoShapeCreate, ...args: any[]) {
    opLog("ADD_SHAPE", shape);
    return api.addShapeApi(shape, ...args);
  }

  const addShapeAndEdit = async (
    shape: GeoShapeCreate,
    onSuccess: (x: GeoShapeMetadata) => void
  ) => {
    opLog("ADD_SHAPE", shape);
    api.addShapeApi(shape as any, {
      onSuccess: (data: any) => {
        const geoshape = data as GeoShape;
        const { properties } = geoshape.geojson;
        const metadata = {
          properties,
          uuid: geoshape.uuid,
          name: geoshape.name,
          created_at: geoshape.created_at,
          updated_at: geoshape.updated_at,
        } as GeoShapeMetadata;
        onSuccess(metadata);
      },
    });
  };

  function deleteShapes(shapeIds: string[], ...args: any[]) {
    opLog("DELETE_SHAPES", shapeIds);
    return api.deleteShapesApi(shapeIds, ...args);
  }

  function updateShape(update: GeoShapeUpdate, params: any) {
    opLog("UPDATE_SHAPE", update);
    return api.updateShapeApi(update, params);
  }

  return (
    <GeoShapeContext.Provider
      value={{
        shapeMetadata: state.shapeMetadata,
        shapeMetadataIsLoading: state.shapeMetadataIsLoading,
        shapeMetadataError: state.shapeMetadataError,
        numShapes: state.numShapes,
        numShapesIsLoading: state.numShapesIsLoading,
        numShapesError: state.numShapesError,
        updateLoading:
          state.shapeAddLoading || state.shapeUpdateLoading || false,
        tileCacheKey: state.tileCacheKey,
        addShape,
        deleteShapes,
        updateShape,
        bulkAddShapes,
        bulkAddFromSplit,
        addShapeAndEdit,
        updatedShapeIds: state.updatedShapeIds,
      }}
    >
      {children}
    </GeoShapeContext.Provider>
  );
};
