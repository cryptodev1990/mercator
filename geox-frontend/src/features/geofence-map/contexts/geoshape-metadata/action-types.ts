import { GeoShapeMetadata, Namespace } from "../../../../client";

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
      type: "UPDATE_NAMESPACE_ERROR";
      error: Error;
    };
