import { Dispatch, useEffect, useState } from "react";
import { GeoShape, ShapeCountResponse } from "../../../../client";
import {
  useAddShapeMutation,
  useBulkAddShapesMutation,
  useBulkDeleteShapesMutation,
  useUpdateShapeMutation,
} from "../../hooks/use-openapi-hooks";
import { Action } from "./action-types";

export const useApi = (dispatch: Dispatch<Action>) => {
  const {
    mutate: addShapeApi,
    data: addShapeResponse,
    isLoading: addShapeIsLoading,
    error: addShapeError,
    isSuccess: addShapeIsSuccess,
  } = useAddShapeMutation();

  const [preferList, setPreferList] = useState(false);

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
  }, [addShapeIsLoading, addShapeError, addShapeIsSuccess]);

  const {
    mutate: deleteShapesApi,
    isLoading: deleteShapesIsLoading,
    error: deleteShapesError,
    isSuccess: deleteShapesIsSuccess,
    variables: deletedUuids,
  } = useBulkDeleteShapesMutation();

  useEffect(() => {
    if (deleteShapesIsLoading === false && deletedUuids !== undefined) {
      dispatch({
        type: "DELETE_SHAPES_LOADING",
        deletedShapeIds: deletedUuids,
      });
    }
    if (deleteShapesIsLoading === false && deleteShapesIsSuccess) {
      dispatch({
        type: "DELETE_SHAPES_SUCCESS",
      });
    }
    if (deleteShapesError !== null) {
      dispatch({ type: "DELETE_SHAPES_ERROR", error: deleteShapesError });
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
    if (updateShapeIsSuccess) {
      dispatch({
        type: "UPDATE_SHAPE_SUCCESS",
        updatedShapeIds: [updateShapeResponse.uuid],
        updatedShape: updateShapeResponse,
      });
    } else if (updateShapeIsLoading === false && updateShapeError !== null) {
      dispatch({ type: "UPDATE_SHAPE_ERROR", error: updateShapeError });
    }
  }, [updateShapeIsLoading, updateShapeError, updateShapeIsSuccess]);

  const {
    mutate: bulkAddShapesApi,
    isLoading: bulkAddShapesIsLoading,
    error: bulkAddShapesError,
    isSuccess: bulkAddShapesIsSuccess,
    variables: bulkAddShapesVars,
    data: bulkAddShapesResponse,
  } = useBulkAddShapesMutation(preferList);

  useEffect(() => {
    if (bulkAddShapesIsLoading) {
      dispatch({
        type: "BULK_ADD_SHAPES_LOADING",
        updatedShapes: bulkAddShapesVars ?? [],
      });
    } else if (
      bulkAddShapesIsLoading === false &&
      bulkAddShapesError !== null
    ) {
      dispatch({ type: "BULK_ADD_SHAPES_ERROR", error: bulkAddShapesError });
    } else if (bulkAddShapesIsSuccess) {
      if ((bulkAddShapesResponse as ShapeCountResponse).num_shapes) {
        console.warn("New additions were not reflected in optimistic updates");
        dispatch({
          type: "BULK_ADD_SHAPES_SUCCESS",
          updatedShapeIds: [],
          updatedShapes: [],
        });
      } else if ((bulkAddShapesResponse as GeoShape[]).length > 0) {
        dispatch({
          type: "BULK_ADD_SHAPES_SUCCESS",
          updatedShapeIds: (bulkAddShapesResponse as GeoShape[]).map(
            (shape) => shape.uuid
          ),
          updatedShapes: bulkAddShapesResponse as GeoShape[],
        });
      }
    }
  }, [bulkAddShapesIsLoading, bulkAddShapesError, bulkAddShapesIsSuccess]);

  return {
    bulkAddShapesApi,
    setPreferList,
    addShapeApi,
    deleteShapesApi,
    updateShapeApi,
  };
};
