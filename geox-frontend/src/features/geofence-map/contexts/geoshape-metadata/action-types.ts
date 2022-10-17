import { GeoShapeMetadata, Namespace } from "../../../../client";

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
    };
