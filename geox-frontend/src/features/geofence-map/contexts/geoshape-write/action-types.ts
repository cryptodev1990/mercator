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
      error: Error;
    }
  | {
      type: "SET_ACTIVE_NAMESPACE";
      namespace: Namespace | null;
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
      error: Error;
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
      error: Error;
    }
  | {
      type: "DELETE_SHAPES_LOADING";
      uuids: string[];
    }
  | {
      type: "DELETE_SHAPES_SUCCESS";
      uuid: string;
      updatedShapeIds: string[];
    }
  | {
      type: "DELETE_SHAPES_ERROR";
      error: Error;
    }
  | {
      type: "UPDATE_SHAPE_LOADING";
    }
  | {
      type: "UPDATE_SHAPE_SUCCESS";
      updatedShapeIds: string[];
      updatedShape: GeoShape | null;
    }
  | {
      type: "UPDATE_SHAPE_ERROR";
      error: Error;
    }
  | {
      type: "BULK_ADD_SHAPES_LOADING";
    }
  | {
      type: "BULK_ADD_SHAPES_SUCCESS";
      updatedShapeIds: string[];
    }
  | {
      type: "BULK_ADD_SHAPES_ERROR";
      error: Error;
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
