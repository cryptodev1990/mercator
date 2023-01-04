import { createContext, Dispatch, useEffect, useReducer } from "react";
import toast from "react-hot-toast";
import { useMutation, useQueryClient } from "react-query";
import {
  GeoShapeMetadata,
  Namespace,
  NamespaceCreate,
  NamespacesService,
} from "../../../../client";
import { aggressiveLog } from "../../../../common/aggressive-log";
import { useGetNamespaces } from "../../hooks/use-openapi-hooks";
import { Action } from "./action-types";
import { geoshapeReducer, initialState, State } from "./reducer";
import {
  useAddNamespaceMutation,
  useDeleteNamespaceMutation,
} from "./use-openapi";

export interface IGeoShapeMetadataContext {
  // API call - get all shape metadata (shape minus geometry)
  // namespaces
  activeNamespaces: Namespace[];
  visibleNamespaces: Namespace[];
  // API call - num shapes
  numShapes: number | null;
  setActiveNamespaces: (namespaces: Namespace[]) => void;
  setVisibleNamespaces: (namespaces: Namespace[]) => void;
  // namespace writes
  addNamespace: (namespace: NamespaceCreate) => void;
  removeNamespace: (id: Namespace["id"]) => void;
  updateNamespace: ({
    namespaceId,
    namespace,
  }: {
    namespaceId: Namespace["id"];
    namespace: Partial<Namespace>;
  }) => void;
}

export const GeoShapeMetadataContext = createContext<IGeoShapeMetadataContext>({
  activeNamespaces: [],
  setActiveNamespaces: () => {},
  visibleNamespaces: [],
  setVisibleNamespaces: async () => {},
  numShapes: null,
  // namespace writes
  addNamespace: async () => {},
  removeNamespace: async () => {},
  updateNamespace: async () => {},
});

GeoShapeMetadataContext.displayName = "GeoShapeMetadataContext";

export const GeoShapeMetadataProvider = ({ children }: { children: any }) => {
  const [state, dispatch]: [State, Dispatch<Action>] = useReducer(
    aggressiveLog(geoshapeReducer, "geoshape-metadata"),
    initialState
  );
  const qc = useQueryClient();
  // run operations only on the first successful fetch

  const { data: allNamespaces } = useGetNamespaces();

  // on the initial load of the data, set the active namespaces to the default namespaces

  useEffect(() => {
    const lastVisibleNamespaces = localStorage.getItem("lastVisibleNamespaces");
    if (lastVisibleNamespaces?.length) {
      const lastVisibleNamespacesParsed = JSON.parse(lastVisibleNamespaces);
      // verify current namespaces and new namespaces are not the same
      const matched =
        lastVisibleNamespacesParsed
          .map((n: Namespace) => n.id)
          .sort()
          .join(",") ===
        state.visibleNamespaces
          .map((n: Namespace) => n.id)
          .sort()
          .join(",");

      if (!matched) {
        console.log("setting visible namespaces");
        dispatch({
          type: "SET_VISIBLE_NAMESPACES",
          namespaces: lastVisibleNamespacesParsed,
        });
      }
    }
    if (allNamespaces) {
      const justUseDefault = allNamespaces.find((ns) => ns.is_default);
      dispatch({
        type: "SET_VISIBLE_NAMESPACES",
        // @ts-ignore
        namespaces: justUseDefault ? [justUseDefault] : [],
      });
    }
  }, [allNamespaces]);

  useEffect(() => {
    if (!state.visibleNamespaces || state.visibleNamespaces.length === 0) {
      return;
    }
    localStorage.setItem(
      "lastVisibleNamespaces",
      JSON.stringify(state.visibleNamespaces)
    );
  }, [state.visibleNamespaces]);

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
    addNamespaceMutation(namespace, {
      onSuccess: async (result) => {
        await qc.cancelQueries(["geofencer"]);

        const previousNamespaces: Namespace[] | undefined = qc.getQueryData([
          "geofencer",
        ]);

        if (previousNamespaces) {
          qc.setQueryData(["geofencer"], [...previousNamespaces, result]);
        }
      },
      onError: (error: any) => {
        toast.error(error.message);
      },
    });
  }

  const { mutate: deleteNamespaceMutation } = useDeleteNamespaceMutation();
  function removeNamespace(id: Namespace["id"]) {
    deleteNamespaceMutation(id, {
      onSuccess: async (data) => {
        await qc.cancelQueries(["geofencer"]);

        const previousNamespaces: Namespace[] | undefined = qc.getQueryData([
          "geofencer",
        ]);

        if (previousNamespaces) {
          qc.setQueryData(
            ["geofencer"],
            previousNamespaces.filter((x: Namespace) => x.id !== id)
          );
        }
      },
      onError: () => {
        toast.error("Error occured deleting namespace");
      },
    });
  }

  const { mutate: updateNamespaceMutation } = useMutation(
    NamespacesService.patchNamespacesGeofencerNamespacesNamespaceIdPatch
  );

  function updateNamespace(data: {
    namespaceId: Namespace["id"];
    namespace: Partial<Namespace>;
  }) {
    updateNamespaceMutation(data, {
      onSuccess: async (response) => {
        await qc.cancelQueries(["geofencer"]);

        const previousNamespaces: Namespace[] | undefined = qc.getQueryData([
          "geofencer",
        ]);

        if (previousNamespaces) {
          qc.setQueryData(
            ["geofencer"],
            previousNamespaces.map((x: any) =>
              x.id === data.namespaceId ? response : x
            )
          );
        }
      },
      onError: () => {
        toast.error("Error occured deleting namespace");
      },
    });
  }

  return (
    <GeoShapeMetadataContext.Provider
      value={{
        activeNamespaces: state.activeNamespaces,
        visibleNamespaces: state.visibleNamespaces,
        setActiveNamespaces,
        setVisibleNamespaces,
        numShapes: allNamespaces?.flatMap((x) => x.shapes ?? []).length ?? null,
        addNamespace,
        removeNamespace,
        updateNamespace,
      }}
    >
      {children}
    </GeoShapeMetadataContext.Provider>
  );
};
