import { useEffect } from "react";
import {
  useAddShapeMutation,
  useBulkAddShapesMutation,
  useBulkDeleteShapesMutation,
  useUpdateShapeMutation,
} from "../../hooks/use-openapi-hooks";

export const useApi = (dispatch: any) => {
  const {
    mutate: addShapeApi,
    data: addShapeResponse,
    isLoading: addShapeIsLoading,
    error: addShapeError,
    isSuccess: addShapeIsSuccess,
  } = useAddShapeMutation();

  useEffect(() => {
    if (addShapeIsLoading === false && addShapeError !== null) {
      dispatch({ type: "ADD_SHAPE_ERROR", error: addShapeError });
    } else if (addShapeIsSuccess) {
      dispatch({
        type: "ADD_SHAPE_SUCCESS",
        updatedShapeIds: [addShapeResponse.uuid],
        updatedShape: addShapeResponse,
      });
    }
  }, [
    addShapeIsLoading,
    addShapeError,
    addShapeIsSuccess,
    addShapeResponse,
    dispatch,
  ]);

  const {
    mutate: deleteShapesApi,
    isLoading: deleteShapesIsLoading,
    error: deleteShapesError,
    isSuccess: deleteShapesIsSuccess,
    variables: deletedUuids,
  } = useBulkDeleteShapesMutation();

  useEffect(() => {
    if (deleteShapesError !== null) {
      dispatch({ type: "DELETE_SHAPES_ERROR", error: deleteShapesError });
    } else if (deleteShapesIsSuccess) {
      dispatch({
        type: "DELETE_SHAPES_SUCCESS",
        updatedShapeIds: deletedUuids || [],
      });
    }
  }, [
    deleteShapesIsLoading,
    deleteShapesError,
    deleteShapesIsSuccess,
    dispatch,
    deletedUuids,
  ]);

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
  }, [
    updateShapeIsLoading,
    updateShapeError,
    updateShapeIsSuccess,
    dispatch,
    updateShapeResponse,
  ]);

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
  }, [
    bulkAddShapesIsLoading,
    bulkAddShapesError,
    bulkAddShapesIsSuccess,
    dispatch,
  ]);

  return {
    bulkAddShapesApi,
    addShapeApi,
    deleteShapesApi,
    updateShapeApi,
  };
};
