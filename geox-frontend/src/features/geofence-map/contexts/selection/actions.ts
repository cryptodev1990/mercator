import { Feature } from "@turf/helpers";
import { GeoShapeMetadata } from "client";

export type Action =
  | {
      type: "ADD_SHAPES_TO_SELECTED_SHAPES";
      selectedShapes: Feature[];
    }
  | {
      type: "REMOVE_SHAPE_FROM_SELECTED_SHAPES";
      shapesUuids: GeoShapeMetadata["uuid"];
    }
  | { type: "RESET_SELECTION" };

export const addShapesToSelectedShapesAction = (shape: Feature[]): Action => ({
  type: "ADD_SHAPES_TO_SELECTED_SHAPES",
  selectedShapes: shape,
});

export const removeShapeFromSelectedShapesAction = (uuid: string): Action => ({
  type: "REMOVE_SHAPE_FROM_SELECTED_SHAPES",
  shapesUuids: uuid,
});

export const clearSelectedShapesAction = (): Action => ({
  type: "RESET_SELECTION",
});
