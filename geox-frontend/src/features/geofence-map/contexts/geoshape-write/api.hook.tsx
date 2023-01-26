import { Dispatch, useEffect, useState } from "react";
import toast from "react-hot-toast";
import { GeoShape, ShapeCountResponse } from "../../../../client";
import {
  useAddShapeMutation,
  useBulkAddShapesMutation,
  useBulkDeleteShapesMutation,
} from "../../hooks/use-openapi-hooks";
import { Action } from "./action-types";
import simplur from "simplur";

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
      dispatch({ type: "SET_LOADING", value: false });
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
      toast.loading("Deleting shapes...");
      dispatch({
        type: "DELETE_SHAPES_LOADING",
        deletedShapeIds: deletedUuids,
      });
    }
    if (deleteShapesIsLoading === false && deleteShapesIsSuccess) {
      toast.dismiss();
      toast.success(simplur`${deletedUuids?.length} shape[|s] deleted`);
    }
    if (deleteShapesError !== null) {
      toast.error("Error with deletion. Please try again.");
    }
  }, [deleteShapesIsLoading, deleteShapesError, deleteShapesIsSuccess]);

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
        updatedShapes: bulkAddShapesVars?.shapes ?? [],
      });
    } else if (
      bulkAddShapesIsLoading === false &&
      bulkAddShapesError !== null
    ) {
      dispatch({ type: "SET_LOADING", value: false });
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
  };
};
