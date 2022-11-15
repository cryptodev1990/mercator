import { createContext, Dispatch, useEffect, useReducer } from "react";
import { useQueryClient } from "react-query";
import {
  GeoShapeMetadata,
  Namespace,
  NamespaceCreate,
  NamespaceResponse,
  NamespacesService,
  NamespaceUpdate,
} from "../../../../client";
import { aggressiveLog } from "../../../../common/aggressive-log";
import {
  useGetAllShapesMetadata,
  useNumShapesQuery,
} from "../../hooks/use-openapi-hooks";
import { Action } from "./action-types";
import { geoshapeReducer, initialState, State } from "./reducer";
import {
  useAddNamespaceMutation,
  useDeleteNamespaceMutation,
} from "./use-openapi";

export interface IGeoShapeMetadataContext {
  // API call - get all shape metadata (shape minus geometry)
  shapeMetadata: GeoShapeMetadata[];
  shapeMetadataIsLoading: boolean;
  shapeMetadataError: Error | null;
  // namespaces
  namespaces: Namespace[];
  activeNamespaces: Namespace[];
  visibleNamepaces: Namespace[];
  // API call - num shapes
  numShapes: number | null;
  numShapesIsLoading: boolean;
  numShapesError: Error | null;
  setActiveNamespaces: (namespaces: Namespace[]) => void;
  setVisibleNamespaces: (namespaces: Namespace[]) => void;
  // namespace writes
  addNamespace: (namespace: NamespaceCreate) => void;
  removeNamespace: (id: Namespace["id"]) => void;
  updateNamespace: (
    namespaceId: Namespace["id"],
    namespace: NamespaceUpdate
  ) => void;
  namespacesError: Error | null;
}

export const GeoShapeMetadataContext = createContext<IGeoShapeMetadataContext>({
  shapeMetadata: [],
  shapeMetadataIsLoading: false,
  shapeMetadataError: null,
  namespaces: [],
  activeNamespaces: [],
  setActiveNamespaces: () => {},
  visibleNamepaces: [],
  setVisibleNamespaces: async () => {},
  numShapes: null,
  numShapesIsLoading: false,
  numShapesError: null,
  // namespace writes
  addNamespace: async () => {},
  removeNamespace: async () => {},
  updateNamespace: async () => {},
  namespacesError: null,
});

GeoShapeMetadataContext.displayName = "GeoShapeMetadataContext";

export const GeoShapeMetadataProvider = ({ children }: { children: any }) => {
  const [state, dispatch]: [State, Dispatch<Action>] = useReducer(
    aggressiveLog(geoshapeReducer, "geoshape-metadata"),
    initialState
  );
  const qc = useQueryClient();

  const {
    data: numShapesPayload,
    isLoading: numShapesIsLoading,
    error: numShapesError,
    isSuccess: numShapesIsSuccess,
  } = useNumShapesQuery();

  useEffect(() => {
    if (numShapesError !== null) {
      dispatch({
        type: "FETCH_NUM_SHAPES_ERROR",
        error: numShapesError as any,
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
    if (shapeMetadataError !== null) {
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

  function setActiveNamespaces(namespaces: Namespace[]) {
    dispatch({
      type: "SET_ACTIVE_NAMESPACES",
      namespaces,
    });
  }

  function setVisibleNamespaces(namespaces: Namespace[]) {
    dispatch({
      type: "SET_VISIBLE_NAMESPACES",
      namespaces,
    });
  }

  const { mutate: addNamespaceMutation } = useAddNamespaceMutation();

  function addNamespace(namespace: NamespaceCreate) {
    dispatch({
      type: "ADD_NAMESPACE_LOADING",
      namespace,
    });
    addNamespaceMutation(namespace, {
      onSuccess: (data) => {
        dispatch({
          type: "ADD_NAMESPACE_SUCCESS",
          payload: data,
        });
        qc.fetchQuery("geofencer");
      },
      onError: (error) => {
        dispatch({
          type: "ADD_NAMESPACE_ERROR",
          error: error as Error,
        });
      },
    });
  }

  const { mutate: deleteNamespaceMutation } = useDeleteNamespaceMutation();
  function removeNamespace(id: Namespace["id"]) {
    dispatch({
      type: "DELETE_NAMESPACE_LOADING",
      id,
    });
    deleteNamespaceMutation(id, {
      onSuccess: (data) => {
        dispatch({
          type: "DELETE_NAMESPACE_SUCCESS",
        });
        qc.fetchQuery("geofencer");
      },
      onError: (error) => {
        dispatch({
          type: "DELETE_NAMESPACE_ERROR",
          error: error as Error,
        });
      },
    });
  }

  function updateNamespace(
    namespaceId: Namespace["id"],
    namespace: NamespaceUpdate
  ) {
    dispatch({
      type: "UPDATE_NAMESPACE_LOADING",
      namespace,
    });
    // TODO this is not a hook because I can't figure out
    // how to get this multiparameter call to work with react-query
    NamespacesService.patchNamespacesGeofencerNamespacesNamespaceIdPatch(
      namespaceId,
      namespace
    )
      .then((data: NamespaceResponse) => {
        dispatch({
          type: "UPDATE_NAMESPACE_SUCCESS",
          payload: data,
        });
        qc.fetchQuery("geofencer");
      })
      .catch((error) => {
        dispatch({
          type: "UPDATE_NAMESPACE_ERROR",
          error: error as Error,
        });
      });
  }

  return (
    <GeoShapeMetadataContext.Provider
      value={{
        shapeMetadata: state.shapeMetadata,
        shapeMetadataIsLoading,
        shapeMetadataError: state.shapeMetadataError,
        namespaces: state.namespaces,
        activeNamespaces: state.activeNamespaces,
        visibleNamepaces: state.visibleNamepaces,
        setActiveNamespaces,
        setVisibleNamespaces,
        numShapes: state.numShapes,
        numShapesIsLoading: state.numShapesIsLoading,
        numShapesError: state.numShapesError,
        addNamespace,
        removeNamespace,
        updateNamespace,
        namespacesError: state.namespacesError,
      }}
    >
      {children}
    </GeoShapeMetadataContext.Provider>
  );
};
