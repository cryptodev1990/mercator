import {
  createContext,
  Dispatch,
  useEffect,
  useReducer,
  useState,
} from "react";
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
import { useGetAllShapesMetadata } from "../../hooks/use-openapi-hooks";
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
  visibleNamespaces: Namespace[];
  // API call - num shapes
  numShapes: number | null;
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
  visibleNamespaces: [],
  setVisibleNamespaces: async () => {},
  numShapes: null,
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
  // run operations only on the first successful fetch
  const [initial, setInitial] = useState(true);

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

  // on the initial load of the data, set the active namespaces to the default namespaces
  useEffect(() => {
    if (state.namespaces.length > 0 && initial) {
      setActiveNamespaces([
        state.namespaces.find((x) => x.is_default) ?? state.namespaces[0],
      ]);
      setVisibleNamespaces([
        state.namespaces.find((x) => x.is_default) ?? state.namespaces[0],
      ]);
      setInitial(false);
    }
  }, [state.namespaces]);

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
        visibleNamespaces: state.visibleNamespaces,
        setActiveNamespaces,
        setVisibleNamespaces,
        numShapes: state.shapeMetadata.length,
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
