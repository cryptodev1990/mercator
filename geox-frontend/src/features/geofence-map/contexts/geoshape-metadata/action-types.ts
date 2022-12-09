import {
  GeoShapeMetadata,
  Namespace,
  NamespaceCreate,
  NamespaceUpdate,
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
      type: "SET_ACTIVE_NAMESPACES";
      namespaces: Namespace[];
    }
  | {
      type: "SET_VISIBLE_NAMESPACES";
      namespaces: Namespace[];
    }
  | {
      type: "REFRESH_TILES";
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
      type: "ADD_NAMESPACE_LOADING";
      namespace: NamespaceCreate;
    }
  | {
      type: "UPDATE_NAMESPACE_LOADING";
      namespace: NamespaceUpdate;
    }
  | {
      type: "DELETE_NAMESPACE_LOADING";
      id: Namespace["id"];
    }
  | {
      type: "ADD_NAMESPACE_SUCCESS";
      payload: Namespace;
    }
  | {
      type: "UPDATE_NAMESPACE_SUCCESS";
      payload: Namespace;
    }
  | {
      type: "DELETE_NAMESPACE_SUCCESS";
    }
  | {
      type: "ADD_NAMESPACE_ERROR";
      error: Error;
    }
  | {
      type: "UPDATE_NAMESPACE_ERROR";
      error: Error;
    }
  | {
      type: "DELETE_NAMESPACE_ERROR";
      error: Error;
    };
