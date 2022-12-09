import { GeoShapeMetadata, Namespace } from "../../../../client";
import { Action } from "./action-types";

export interface State {
  shapeMetadata: GeoShapeMetadata[];
  namespaces: Namespace[];
  activeNamespaces: Namespace[];
  visibleNamespaces: Namespace[];
  shapeMetadataIsLoading: boolean;
  shapeMetadataError: Error | null;
  numShapes: number | null;
  numShapesIsLoading: boolean;
  numShapesError: Error | null;
  namespacesError: Error | null;
  refreshTiles: boolean;
}

export const initialState: State = {
  shapeMetadata: [],
  namespaces: [],
  activeNamespaces: [],
  visibleNamespaces: [],
  shapeMetadataIsLoading: false,
  shapeMetadataError: null,
  numShapes: null,
  numShapesIsLoading: false,
  numShapesError: null,
  namespacesError: null,
  refreshTiles: false,
};

export function geoshapeReducer(state: State, action: Action): State {
  switch (action.type) {
    // Shape metadata actions
    case "FETCH_SHAPE_METADATA_LOADING": {
      return {
        ...state,
        shapeMetadataIsLoading: true,
      };
    }
    case "FETCH_SHAPE_METADATA_SUCCESS": {
      return {
        ...state,
        shapeMetadataIsLoading: false,
        shapeMetadata: action.shapeMetadata,
        namespaces: action.namespaces,
      };
    }
    case "FETCH_SHAPE_METADATA_ERROR": {
      return {
        ...state,
        shapeMetadataIsLoading: false,
        shapeMetadataError: action.error,
      };
    }
    // Shape count actions
    case "FETCH_NUM_SHAPES_LOADING": {
      return {
        ...state,
        numShapesIsLoading: true,
      };
    }
    case "FETCH_NUM_SHAPES_SUCCESS": {
      return {
        ...state,
        numShapesIsLoading: false,
        numShapes: action.numShapes,
      };
    }
    case "FETCH_NUM_SHAPES_ERROR": {
      return {
        ...state,
        shapeMetadataIsLoading: false,
        shapeMetadataError: action.error,
      };
    }
    case "SET_ACTIVE_NAMESPACES": {
      return {
        ...state,
        activeNamespaces: action.namespaces,
      };
    }
    case "SET_VISIBLE_NAMESPACES": {
      return {
        ...state,
        visibleNamespaces: action.namespaces,
      };
    }
    case "REFRESH_TILES": {
      return {
        ...state,
        refreshTiles: !state.refreshTiles,
      };
    }
    case "DELETE_NAMESPACE_LOADING": {
      return {
        ...state,
      };
    }
    case "DELETE_NAMESPACE_SUCCESS": {
      return {
        ...state,
      };
    }
    case "UPDATE_NAMESPACE_ERROR":
    case "ADD_NAMESPACE_ERROR":
    case "DELETE_NAMESPACE_ERROR": {
      return {
        ...state,
        namespacesError: action.error,
      };
    }
    default:
      return state;
  }
}
