import { useEffect } from "react";
import { NamespaceResponse } from "../../../../client";
import {
  useAddShapeMutation,
  useBulkAddShapesMutation,
  useBulkDeleteShapesMutation,
  useGetAllShapesMetadata,
  useNumShapesQuery,
  useUpdateShapeMutation,
} from "../../hooks/openapi-hooks";

export const useApi = (dispatch: any) => {
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
        shapeMetadata: remoteShapeMetadata.flatMap((x) => x.shapes),
        namespaces: remoteShapeMetadata.map((x: NamespaceResponse) => {
          delete x.shapes;
          return x;
        }),
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
    data: addShapeResponse,
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
      dispatch({
        type: "ADD_SHAPE_SUCCESS",
        updatedShapeIds: [addShapeResponse.uuid],
        updatedShape: addShapeResponse,
      });
    }
  }, [addShapeIsLoading, addShapeError, addShapeIsSuccess]);

  const {
    mutate: deleteShapesApi,
    isLoading: deleteShapesIsLoading,
    error: deleteShapesError,
    isSuccess: deleteShapesIsSuccess,
    variables: deletedUuids,
  } = useBulkDeleteShapesMutation();

  useEffect(() => {
    if (deleteShapesIsLoading) {
      dispatch({ type: "DELETE_SHAPES_LOADING" });
    } else if (deleteShapesIsLoading === false && deleteShapesError !== null) {
      dispatch({ type: "DELETE_SHAPES_ERROR", error: deleteShapesError });
    } else if (deleteShapesIsSuccess) {
      dispatch({
        type: "DELETE_SHAPES_SUCCESS",
        updatedShapeIds: deletedUuids || [],
      });
    }
  }, [deleteShapesIsLoading, deleteShapesError, deleteShapesIsSuccess]);

  const {
    mutate: updateShapeApi,
    isLoading: updateShapeIsLoading,
    error: updateShapeError,
    isSuccess: updateShapeIsSuccess,
    data: updateShapeResponse,
  } = useUpdateShapeMutation();

  useEffect(() => {
    if (updateShapeIsLoading) {
      dispatch({ type: "UPDATE_SHAPE_LOADING" });
    } else if (updateShapeIsLoading === false && updateShapeError !== null) {
      dispatch({ type: "UPDATE_SHAPE_ERROR", error: updateShapeError });
    } else if (updateShapeIsSuccess) {
      dispatch({
        type: "UPDATE_SHAPE_SUCCESS",
        updatedShapeIds: [updateShapeResponse.uuid],
        updatedShape: updateShapeResponse,
      });
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

  return {
    bulkAddShapesApi,
    addShapeApi,
    deleteShapesApi,
    updateShapeApi,
    shapeMetadataIsLoading,
    shapeMetadataError,
    numShapesIsLoading,
    numShapesError,
  };
};
