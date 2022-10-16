import { createContext, Dispatch, useEffect, useReducer } from "react";
import { UseMutateFunction } from "react-query";
import {
  GeoShape,
  GeoShapeCreate,
  GeoShapeMetadata,
  GeoShapeUpdate,
  Namespace,
  ShapeCountResponse,
} from "../../../../client";
import { aggressiveLog } from "../../../../common/aggressive-log";
import { useApi } from "./api.hook";
import {
  Action,
  geoshapeReducer,
  initialState,
  State,
  UndoLogRecord,
} from "./geoshape.reducer";

export interface GeoShapeContextI {
  // API call - get all shape metadata (shape minus geometry)
  shapeMetadata: GeoShapeMetadata[];
  shapeMetadataIsLoading: boolean;
  shapeMetadataError: Error | null;
  // namespaces
  namespaces: Namespace[];
  activeNamespace: Namespace | null;
  visibleNamepaces: Namespace[];
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
  updatedShape: GeoShape | null;
  setActiveNamespace: (namespace: Namespace | null) => void;
  setVisibleNamespaces: any;
}

export const GeoShapeContext = createContext<GeoShapeContextI>({
  shapeMetadata: [],
  shapeMetadataIsLoading: false,
  shapeMetadataError: null,
  namespaces: [],
  activeNamespace: null,
  visibleNamepaces: [],
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
  updatedShape: null,
  setActiveNamespace: () => {},
  setVisibleNamespaces: async () => {},
});

GeoShapeContext.displayName = "GeoShapeContext";

export const GeoShapeProvider = ({ children }: { children: any }) => {
  const [state, dispatch]: [State, Dispatch<Action>] = useReducer(
    aggressiveLog(geoshapeReducer),
    initialState
  );
  const api = useApi(dispatch);

  function opLog(op: UndoLogRecord["op"], payload: any) {
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
      onSuccess: (data: GeoShape) => {
        const { properties } = data.geojson;
        const metadata = {
          properties,
          uuid: data.uuid,
          name: data.name,
          created_at: data.created_at,
          updated_at: data.updated_at,
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

  function setActiveNamespace(namespace: Namespace | null) {
    dispatch({
      type: "SET_ACTIVE_NAMESPACE",
      namespace,
    });
  }

  function setVisibleNamespaces(namespaces: Namespace[]) {
    dispatch({
      type: "SET_VISIBLE_NAMESPACES",
      namespaces,
    });
  }

  return (
    <GeoShapeContext.Provider
      value={{
        shapeMetadata: state.shapeMetadata,
        shapeMetadataIsLoading: state.shapeMetadataIsLoading,
        shapeMetadataError: state.shapeMetadataError,
        namespaces: state.namespaces,
        activeNamespace: state.activeNamespace,
        visibleNamepaces: state.visibleNamepaces,
        setActiveNamespace,
        setVisibleNamespaces,
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
        updatedShape: state.updatedShape,
      }}
    >
      {children}
    </GeoShapeContext.Provider>
  );
};
