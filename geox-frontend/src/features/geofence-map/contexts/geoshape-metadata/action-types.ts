import { GeoShapeMetadata, Namespace } from "../../../../client";

export type Action =
  | {
      type: "SET_ACTIVE_NAMESPACES";
      namespaces: string[];
    }
  | {
      type: "SET_VISIBLE_NAMESPACES";
      namespaces: string[];
    }
  | {
      type: "UPDATE_NAMESPACE_ERROR";
      error: Error;
    };
