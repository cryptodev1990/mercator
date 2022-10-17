import { createContext, Dispatch, useEffect, useReducer } from "react";
import {
  GeoShapeMetadata,
  Namespace,
  NamespaceResponse,
} from "../../../../client";
import { aggressiveLog } from "../../../../common/aggressive-log";
import {
  useGetAllShapesMetadata,
  useNumShapesQuery,
} from "../../hooks/use-openapi-hooks";
import { Action } from "./action-types";
import { geoshapeReducer, initialState, State } from "./reducer";

export interface IGeoShapeMetadataContext {
  // API call - get all shape metadata (shape minus geometry)
  shapeMetadata: GeoShapeMetadata[];
  shapeMetadataIsLoading: boolean;
  shapeMetadataError: Error | null;
  // namespaces
  namespaces: Namespace[];
  activeNamespace: Namespace | null;
  visibleNamepaces: Namespace[];
  // API call - num shapes
  numShapes: number | null;
  numShapesIsLoading: boolean;
  numShapesError: Error | null;
  setActiveNamespace: (namespace: Namespace | null) => void;
  setVisibleNamespaces: any;
}

export const GeoShapeMetadataContext = createContext<IGeoShapeMetadataContext>({
  shapeMetadata: [],
  shapeMetadataIsLoading: false,
  shapeMetadataError: null,
  namespaces: [],
  activeNamespace: null,
  setActiveNamespace: () => {},
  visibleNamepaces: [],
  setVisibleNamespaces: async () => {},
  numShapes: null,
  numShapesIsLoading: false,
  numShapesError: null,
});

GeoShapeMetadataContext.displayName = "GeoShapeMetadataContext";

export const GeoShapeMetadataProvider = ({ children }: { children: any }) => {
  const [state, dispatch]: [State, Dispatch<Action>] = useReducer(
    aggressiveLog(geoshapeReducer, "geoshape-metadata"),
    initialState
  );

  const {
    data: numShapesPayload,
    isLoading: numShapesIsLoading,
    error: numShapesError,
    isSuccess: numShapesIsSuccess,
  } = useNumShapesQuery();

  useEffect(() => {
    if (numShapesIsLoading) {
      dispatch({ type: "FETCH_NUM_SHAPES_LOADING" });
    } else if (numShapesError !== null) {
      dispatch({
        type: "FETCH_NUM_SHAPES_ERROR",
        error: numShapesError as Error,
      });
    } else if (numShapesIsSuccess) {
      dispatch({
        type: "FETCH_NUM_SHAPES_SUCCESS",
        numShapes: numShapesPayload?.num_shapes || 0,
      });
    }
  }, [
    numShapesPayload,
    numShapesIsLoading,
    numShapesError,
    numShapesIsSuccess,
  ]);

  const {
    data: remoteShapeMetadata,
    isLoading: shapeMetadataIsLoading,
    error: shapeMetadataError,
    isSuccess: shapeMetadataIsSuccess,
  } = useGetAllShapesMetadata();

  useEffect(() => {
    if (shapeMetadataIsLoading) {
      dispatch({ type: "FETCH_SHAPE_METADATA_LOADING" });
    } else if (shapeMetadataError !== null) {
      dispatch({
        type: "FETCH_SHAPE_METADATA_ERROR",
        error: shapeMetadataError as Error,
      });
    } else if (shapeMetadataIsSuccess) {
      dispatch({
        type: "FETCH_SHAPE_METADATA_SUCCESS",
        shapeMetadata: remoteShapeMetadata.flatMap((x) => x.shapes ?? []),
        namespaces: remoteShapeMetadata.map((x: NamespaceResponse) => {
          delete x.shapes;
          return x;
        }),
      });
    }
  }, [
    remoteShapeMetadata,
    shapeMetadataIsLoading,
    shapeMetadataError,
    shapeMetadataIsSuccess,
  ]);

  function setActiveNamespace(namespace: Namespace | null) {
    dispatch({
      type: "SET_ACTIVE_NAMESPACE",
      namespace,
    });
  }

  function setVisibleNamespaces(namespaces: Namespace[]) {
    dispatch({
      type: "SET_VISIBLE_NAMESPACES",
      namespaces,
    });
  }

  return (
    <GeoShapeMetadataContext.Provider
      value={{
        shapeMetadata: state.shapeMetadata,
        shapeMetadataIsLoading: state.shapeMetadataIsLoading,
        shapeMetadataError: state.shapeMetadataError,
        namespaces: state.namespaces,
        activeNamespace: state.activeNamespace,
        visibleNamepaces: state.visibleNamepaces,
        setActiveNamespace,
        setVisibleNamespaces,
        numShapes: state.numShapes,
        numShapesIsLoading: state.numShapesIsLoading,
        numShapesError: state.numShapesError,
      }}
    >
      {children}
    </GeoShapeMetadataContext.Provider>
  );
};
