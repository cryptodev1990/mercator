import { createContext, useEffect, useReducer } from "react";
import { UseMutateFunction } from "react-query";
import {
  GeoShape,
  GeoShapeCreate,
  GeoShapeMetadata,
  GeoShapeUpdate,
  ShapeCountResponse,
} from "../../../../client";
import { aggressiveLog } from "../../../../common/aggressive-log";
import {
  useAddShapeMutation,
  useBulkAddShapesMutation,
  useBulkDeleteShapesMutation,
  useGetAllShapesMetadata,
  useNumShapesQuery,
  useUpdateShapeMutation,
} from "../../hooks/openapi-hooks";
import { geoshapeReducer, initialState } from "./geoshape.reducer";

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
});

GeoShapeContext.displayName = "GeoShapeContext";

export const GeoShapeProvider = ({ children }: { children: any }) => {
  const [state, dispatch] = useReducer(
    aggressiveLog(geoshapeReducer),
    initialState
  );

  const {
    data: numShapesPayload,
    isLoading: numShapesIsLoading,
    error: numShapesError,
    isSuccess: numShapesIsSuccess,
  } = useNumShapesQuery();

  useEffect(() => {
    if (numShapesIsLoading) {
      dispatch({ type: "FETCH_NUM_SHAPES_LOADING" });
    } else if (numShapesError !== null) {
      dispatch({
        type: "FETCH_NUM_SHAPES_ERROR",
        error: numShapesError,
      });
    } else if (numShapesIsSuccess) {
      dispatch({
        type: "FETCH_NUM_SHAPES_SUCCESS",
        numShapes: numShapesPayload?.num_shapes || 0,
      });
    }
  }, [
    numShapesPayload,
    numShapesIsLoading,
    numShapesError,
    numShapesIsSuccess,
  ]);

  const {
    data: remoteShapeMetadata,
    isLoading: shapeMetadataIsLoading,
    error: shapeMetadataError,
    isSuccess: shapeMetadataIsSuccess,
  } = useGetAllShapesMetadata();

  useEffect(() => {
    if (shapeMetadataIsLoading) {
      dispatch({ type: "FETCH_SHAPE_METADATA_LOADING" });
    } else if (shapeMetadataError !== null) {
      dispatch({
        type: "FETCH_SHAPE_METADATA_ERROR",
        error: shapeMetadataError,
      });
    } else if (shapeMetadataIsSuccess) {
      dispatch({
        type: "FETCH_SHAPE_METADATA_SUCCESS",
        shapeMetdata: remoteShapeMetadata || [],
      });
    }
  }, [
    remoteShapeMetadata,
    shapeMetadataIsLoading,
    shapeMetadataError,
    shapeMetadataIsSuccess,
  ]);

  const {
    mutate: addShapeApi,
    isLoading: addShapeIsLoading,
    error: addShapeError,
    isSuccess: addShapeIsSuccess,
  } = useAddShapeMutation();

  useEffect(() => {
    if (addShapeIsLoading) {
      dispatch({ type: "ADD_SHAPE_LOADING" });
    } else if (addShapeIsLoading === false && addShapeError !== null) {
      dispatch({ type: "ADD_SHAPE_ERROR", error: addShapeError });
    } else if (addShapeIsSuccess) {
      dispatch({ type: "ADD_SHAPE_SUCCESS" });
    }
  }, [addShapeIsLoading, addShapeError, addShapeIsSuccess]);

  const {
    mutate: deleteShapesApi,
    isLoading: deleteShapesIsLoading,
    error: deleteShapesError,
    isSuccess: deleteShapesIsSuccess,
  } = useBulkDeleteShapesMutation();

  useEffect(() => {
    if (deleteShapesIsLoading) {
      dispatch({ type: "DELETE_SHAPES_LOADING" });
    } else if (deleteShapesIsLoading === false && deleteShapesError !== null) {
      dispatch({ type: "DELETE_SHAPES_ERROR", error: deleteShapesError });
    } else if (deleteShapesIsSuccess) {
      dispatch({ type: "DELETE_SHAPES_SUCCESS" });
    }
  }, [deleteShapesIsLoading, deleteShapesError, deleteShapesIsSuccess]);

  const {
    mutate: updateShapeApi,
    isLoading: updateShapeIsLoading,
    error: updateShapeError,
    isSuccess: updateShapeIsSuccess,
  } = useUpdateShapeMutation();

  useEffect(() => {
    if (updateShapeIsLoading) {
      dispatch({ type: "UPDATE_SHAPE_LOADING" });
    } else if (updateShapeIsLoading === false && updateShapeError !== null) {
      dispatch({ type: "UPDATE_SHAPE_ERROR", error: updateShapeError });
    } else if (updateShapeIsSuccess) {
      dispatch({ type: "UPDATE_SHAPE_SUCCESS" });
    }
  }, [updateShapeIsLoading, updateShapeError, updateShapeIsSuccess]);

  const {
    mutate: bulkAddShapesApi,
    isLoading: bulkAddShapesIsLoading,
    error: bulkAddShapesError,
    isSuccess: bulkAddShapesIsSuccess,
  } = useBulkAddShapesMutation();

  useEffect(() => {
    if (bulkAddShapesIsLoading) {
      dispatch({ type: "BULK_ADD_SHAPES_LOADING" });
    } else if (
      bulkAddShapesIsLoading === false &&
      bulkAddShapesError !== null
    ) {
      dispatch({ type: "BULK_ADD_SHAPES_ERROR", error: bulkAddShapesError });
    } else if (bulkAddShapesIsSuccess) {
      dispatch({ type: "BULK_ADD_SHAPES_SUCCESS" });
    }
  }, [bulkAddShapesIsLoading, bulkAddShapesError, bulkAddShapesIsSuccess]);

  function bulkAddShapes(shapes: GeoShapeCreate[]) {
    dispatch({ type: "OP_LOG_ADD", op: "BULK_ADD_SHAPES", payload: shapes });
    return bulkAddShapesApi(shapes);
  }

  function bulkAddFromSplit(
    shapes: GeoShapeCreate[],
    { onSuccess, onError }: any
  ) {
    dispatch({
      type: "OP_LOG_ADD",
      op: "BULK_ADD_SHAPE_SPLIT",
      payload: shapes,
    });
    return bulkAddShapesApi(shapes, {
      onSuccess,
      onError,
    });
  }

  function addShape(shape: GeoShapeCreate, ...args: any[]) {
    dispatch({ type: "OP_LOG_ADD", op: "ADD_SHAPE", payload: shape });
    return addShapeApi(shape, ...args);
  }

  const addShapeAndEdit = async (
    shape: GeoShapeCreate,
    onSuccess: (x: GeoShapeMetadata) => void
  ) => {
    dispatch({ type: "OP_LOG_ADD", op: "ADD_SHAPE", payload: shape });
    addShapeApi(shape as any, {
      onSuccess: (data: any) => {
        const geoshape = data as GeoShape;
        const metadata = {
          properties: geoshape.geojson.properties,
          ...geoshape,
        } as GeoShapeMetadata;
        onSuccess(metadata);
      },
    });
  };

  function deleteShapes(shapeIds: string[], ...args: any[]) {
    dispatch({ type: "OP_LOG_ADD", op: "DELETE_SHAPES", payload: shapeIds });
    return deleteShapesApi(shapeIds, ...args);
  }

  function updateShape(update: GeoShapeUpdate, params: any) {
    dispatch({
      type: "OP_LOG_ADD",
      op: "UPDATE_SHAPE",
      payload: update,
    });
    return updateShapeApi(update, params);
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
        tileCacheKey: state.tileCacheKey,
        addShape,
        deleteShapes,
        updateShape,
        bulkAddShapes,
        bulkAddFromSplit,
        addShapeAndEdit,
        updateLoading: state.updateLoading,
      }}
    >
      {children}
    </GeoShapeContext.Provider>
  );
};
