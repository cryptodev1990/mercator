import { GeoShape, GeoShapeCreate, Namespace } from "../../../../client";

export type Action =
  | {
      type: "SET_ACTIVE_NAMESPACES";
      namespaces: Namespace[];
    }
  | {
      type: "SET_VISIBLE_NAMESPACES";
      namespaces: Namespace[];
    }
  | {
      type: "CLEAR_OPTIMISTIC_SHAPE_UPDATES";
    }
  | {
      type: "SET_OPTIMISTIC_SHAPE";
      shape: GeoShape;
    }
  // TODO: all the actions below should be removed
  | {
      type: "ADD_SHAPE_LOADING";
      shape: GeoShapeCreate;
    }
  | {
      type: "ADD_SHAPE_SUCCESS";
      updatedShapeIds: string[];
      updatedShape: GeoShape | null;
    }
  | {
      type: "DELETE_SHAPES_LOADING";
      deletedShapeIds: string[];
    }
  | {
      type: "SET_LOADING";
      value: boolean;
    }
  | {
      type: "BULK_ADD_SHAPES_LOADING";
      updatedShapes: GeoShapeCreate[];
    }
  | {
      type: "BULK_ADD_SHAPES_SUCCESS";
      updatedShapeIds: string[];
      updatedShapes: GeoShape[];
    };
