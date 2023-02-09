import { createContext, Dispatch, useEffect, useReducer } from "react";
import toast from "react-hot-toast";
import { useMutation, useQueryClient } from "react-query";
import {
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
  activeNamespaceIDs: string[];
  visibleNamespaceIDs: string[];
  // API call - num shapes
  numShapes: number | null;
  setActiveNamespaceIDs: (namespaceIDs: string[]) => void;
  setVisibleNamespaceIDs: (namespaces: string[]) => void;
  // namespace writes
  addNamespace: (namespace: NamespaceCreate) => void;
  removeNamespace: (id: Namespace["id"]) => void;
}

export const GeoShapeMetadataContext = createContext<IGeoShapeMetadataContext>({
  activeNamespaceIDs: [],
  setActiveNamespaceIDs: () => {},
  visibleNamespaceIDs: [],
  setVisibleNamespaceIDs: async () => {},
  numShapes: null,
  // namespace writes
  addNamespace: async () => {},
  removeNamespace: async () => {},
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
    const lastVisibleNamespaceIDs = localStorage.getItem(
      "lastVisibleNamespaceIDs"
    );
    if (lastVisibleNamespaceIDs?.length) {
      const lastVisibleNamespaceIDsParsed = JSON.parse(lastVisibleNamespaceIDs);
      // verify current namespaces and new namespaces are not the same
      const matched =
        lastVisibleNamespaceIDsParsed.sort().join(",") ===
        state.visibleNamespaceIDs.sort().join(",");

      if (!matched) {
        dispatch({
          type: "SET_VISIBLE_NAMESPACES",
          namespaces: lastVisibleNamespaceIDsParsed,
        });
      }
    }
  }, [allNamespaces]);

  useEffect(() => {
    if (!state.visibleNamespaceIDs) {
      return;
    }
    localStorage.setItem(
      "lastVisibleNamespaceIDs",
      JSON.stringify(state.visibleNamespaceIDs)
    );
  }, [state.visibleNamespaceIDs]);

  function setActiveNamespaceIDs(namespaces: string[]) {
    dispatch({
      type: "SET_ACTIVE_NAMESPACES",
      namespaces: namespaces,
    });
  }

  function setVisibleNamespaceIDs(namespaces: string[]) {
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

        toast.success("Namespace deleted successfully");
      },
      onError: () => {
        toast.error("Error occured deleting namespace");
      },
    });
  }

  return (
    <GeoShapeMetadataContext.Provider
      value={{
        activeNamespaceIDs: state.activeNamespaceIDs,
        visibleNamespaceIDs: state.visibleNamespaceIDs,
        setActiveNamespaceIDs,
        setVisibleNamespaceIDs,
        numShapes: allNamespaces?.flatMap((x) => x.shapes ?? []).length ?? null,
        addNamespace,
        removeNamespace,
      }}
    >
      {children}
    </GeoShapeMetadataContext.Provider>
  );
};
