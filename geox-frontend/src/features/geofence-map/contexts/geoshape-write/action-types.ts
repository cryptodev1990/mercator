import {
  GeoShape,
  GeoShapeCreate,
  GeoShapeMetadata,
  Namespace,
} from "../../../../client";

export type Action =
  | {
      type: "FETCH_SHAPE_METADATA_LOADING";
    }
  | {
      type: "FETCH_SHAPE_METADATA_SUCCESS";
      shapeMetadata: GeoShapeMetadata[];
      namespaces: Namespace[];
    }
  | {
      type: "FETCH_SHAPE_METADATA_ERROR";
      error: any;
    }
  | {
      type: "SET_ACTIVE_NAMESPACES";
      namespaces: Namespace[];
    }
  | {
      type: "SET_VISIBLE_NAMESPACES";
      namespaces: Namespace[];
    }
  | {
      type: "FETCH_NUM_SHAPES_LOADING";
    }
  | {
      type: "FETCH_NUM_SHAPES_SUCCESS";
      numShapes: number;
    }
  | {
      type: "FETCH_NUM_SHAPES_ERROR";
      error: any;
    }
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
      type: "ADD_SHAPE_ERROR";
      error: any;
    }
  | {
      type: "DELETE_SHAPES_LOADING";
      deletedShapeIds: string[];
    }
  | {
      type: "DELETE_SHAPES_SUCCESS";
    }
  | {
      type: "DELETE_SHAPES_ERROR";
      error: any;
    }
  | {
      type: "UPDATE_SHAPE_LOADING";
      shapes: GeoShape[];
    }
  | {
      type: "UPDATE_SHAPE_SUCCESS";
      updatedShapeIds: string[];
      updatedShape: GeoShape | null;
    }
  | {
      type: "UPDATE_SHAPE_ERROR";
      error: any;
    }
  | {
      type: "BULK_ADD_SHAPES_LOADING";
      updatedShapes: GeoShapeCreate[];
    }
  | {
      type: "BULK_ADD_SHAPES_SUCCESS";
      updatedShapeIds: string[];
      updatedShapes: GeoShape[];
    }
  | {
      type: "BULK_ADD_SHAPES_ERROR";
      error: any;
    }
  | {
      type: "OP_LOG_ADD";
      op:
        | "ADD_SHAPE"
        | "DELETE_SHAPES"
        | "UPDATE_SHAPE"
        | "BULK_ADD_SHAPES"
        | "BULK_ADD_SHAPE_SPLIT";
      payload: any;
    }
  | {
      type: "OP_LOG_UNDO" | "OP_LOG_REDO";
      op: any;
      payload: any;
    }
  | {
      type: "SNAPSHOT_START";
      selectedFeatureCollection: any;
    }
  | {
      type: "SNAPSHOT_END";
      selectedFeatureCollection: any;
    }
  | {
      type: "CLEAR_OPTIMISTIC_SHAPE_UPDATES";
    };
