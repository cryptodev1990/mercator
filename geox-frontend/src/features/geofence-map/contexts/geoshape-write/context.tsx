import { difference } from "@turf/turf";
import { ShapesBulkUploadOptions } from "features/geofence-map/types";
import {
  createContext,
  Dispatch,
  useContext,
  useEffect,
  useMemo,
  useReducer,
} from "react";
import { UseMutateFunction } from "react-query";
import {
  GeoShape,
  GeoShapeCreate,
  GeoShapeMetadata,
  ShapeCountResponse,
} from "../../../../client";
import { aggressiveLog } from "../../../../common/aggressive-log";
import { useCursorMode } from "../../hooks/use-cursor-mode";
import { DeckContext } from "../deck-context";
import { Action } from "./actions";
import { useApi } from "./api.hook";
import { reducer, initialState, State } from "./reducer";

export interface IGeoShapeWriteContext {
  updatedShape: GeoShape | null;
  deletedShapeIds: string[];
  optimisticShapeUpdates: GeoShapeCreate[];
  updateLoading: boolean;
  dispatch: Dispatch<Action>;
  // TODO: remove all the context values below this comment
  deleteShapes: UseMutateFunction<
    ShapeCountResponse,
    unknown,
    string[],
    unknown
  >;
  // API call - add shape
  addShape: UseMutateFunction<
    GeoShapeMetadata,
    unknown,
    GeoShapeCreate,
    unknown
  >;
  // API call - bulk add shape
  bulkAddShapes: UseMutateFunction<
    ShapeCountResponse,
    unknown,
    ShapesBulkUploadOptions,
    unknown
  >;
  bulkAddFromSplit: UseMutateFunction<
    GeoShapeCreate[],
    unknown,
    GeoShapeCreate[],
    unknown
  >;
  addShapeAndEdit: any;
  updatedShapeIdSet: Set<string>;
  deletedShapeIdSet: Set<string>;
  updatedShapeIds: string[];
  clearOptimisticShapeUpdates: () => void;
}

export const GeoShapeWriteContext = createContext<IGeoShapeWriteContext>({
  deleteShapes: async () => {},
  addShape: async () => {},
  bulkAddShapes: async () => {},
  bulkAddFromSplit: async () => {},
  updateLoading: false,
  addShapeAndEdit: async () => {},
  updatedShapeIds: [],
  deletedShapeIds: [],
  updatedShape: null,
  optimisticShapeUpdates: [],
  clearOptimisticShapeUpdates: () => {},
  deletedShapeIdSet: new Set(),
  updatedShapeIdSet: new Set(),
  dispatch: () => {},
});

GeoShapeWriteContext.displayName = "GeoShapeWriteContext";

export const GeoShapeWriteContextProvider = ({
  children,
}: {
  children: any;
}) => {
  const [state, dispatch]: [State, Dispatch<Action>] = useReducer(
    aggressiveLog(reducer, "geoshape-write"),
    initialState
  );
  const api = useApi(dispatch);
  const { options } = useCursorMode();
  const { deckRef, setHoveredUuid } = useContext(DeckContext);

  function bulkAddShapes(data: ShapesBulkUploadOptions, ...args: any[]) {
    api.setPreferList(false);
    return api.bulkAddShapesApi(data, ...args);
  }

  useEffect(() => {
    setHoveredUuid(null);
  }, [state.deletedShapeIds]);

  function bulkAddFromSplit(
    shapes: GeoShapeCreate[],
    { onSuccess, onError }: any
  ) {
    api.setPreferList(true);
    return api.bulkAddShapesApi(
      { shapes },
      {
        onSuccess,
        onError,
      }
    );
  }

  const deletedShapeIdSet = useMemo(() => {
    return new Set(state.deletedShapeIds);
  }, [state.deletedShapeIds]);

  const updatedShapeIdSet = useMemo(() => {
    return new Set(state.updatedShapeIds);
  }, [state.updatedShapeIds]);

  function removeOverlapFrom(shape: GeoShapeCreate): GeoShapeCreate {
    const shouldRemoveOverlap =
      options?.denyOverlap &&
      typeof deckRef.current !== "undefined" &&
      deckRef.current.deck &&
      deckRef.current.deck.layerManager;

    // feature remove overlap
    if (shouldRemoveOverlap) {
      const layerManager = deckRef.current.deck.layerManager;
      const mvtLayer = layerManager
        .getLayers()
        .find((x: any) => x.id === "gf-mvt");
      // TODO this produces way more features than it needs to, what gives?
      const currentFeatures = mvtLayer?.getRenderedFeatures();
      if (!currentFeatures) {
        return shape;
      }

      for (let i = 1; i < currentFeatures.length; i++) {
        const feature = currentFeatures[i];
        // ignore if the feature is not a polygon or multipolygon
        if (
          feature.geometry.type !== "Polygon" &&
          feature.geometry.type !== "MultiPolygon"
        ) {
          continue;
        }
        // ignore the feature if it's in our delete list
        if (
          deletedShapeIdSet.has(feature?.properties?.__uuid) ||
          updatedShapeIdSet.has(feature?.properties?.__uuid)
        ) {
          continue;
        }
        const diffShape = difference(shape.geojson as any, feature);
        shape.geojson = diffShape as any;
      }
      // remove optimistic shapes
      for (let i = 0; i < state.optimisticShapeUpdates.length; i++) {
        const optimisticShape = state.optimisticShapeUpdates[i];
        const diffShape = difference(
          shape.geojson as any,
          optimisticShape.geojson as any
        );
        shape.geojson = diffShape as any;
      }
    }
    return shape;
  }

  function addShape(shape: GeoShapeCreate, ...args: any[]) {
    dispatch({ type: "ADD_SHAPE_LOADING", shape });
    return api.addShapeApi(removeOverlapFrom(shape), ...args);
  }

  const addShapeAndEdit = async (
    shape: GeoShapeCreate,
    onSuccess: (x: GeoShapeMetadata) => void
  ) => {
    dispatch({ type: "ADD_SHAPE_LOADING", shape });
    api.addShapeApi(removeOverlapFrom(shape), {
      onSuccess: (data: GeoShape) => {
        const { properties } = data.geojson;
        const metadata = {
          properties,
          uuid: data.uuid,
          name: data.name,
          created_at: data.created_at,
          updated_at: data.updated_at,
        } as GeoShapeMetadata;
        onSuccess(metadata);
      },
    });
  };

  function deleteShapes(shapeIds: string[], ...args: any[]) {
    return api.deleteShapesApi(shapeIds, ...args);
  }

  function clearOptimisticShapeUpdates() {
    dispatch({ type: "CLEAR_OPTIMISTIC_SHAPE_UPDATES" });
  }

  return (
    <GeoShapeWriteContext.Provider
      value={{
        updateLoading: state.loading,
        addShape,
        deleteShapes,
        bulkAddShapes,
        bulkAddFromSplit,
        addShapeAndEdit,
        optimisticShapeUpdates: state.optimisticShapeUpdates,
        updatedShapeIds: state.updatedShapeIds,
        updatedShape: state.updatedShape,
        deletedShapeIds: state.deletedShapeIds,
        clearOptimisticShapeUpdates,
        deletedShapeIdSet,
        updatedShapeIdSet,
        dispatch,
      }}
    >
      {children}
    </GeoShapeWriteContext.Provider>
  );
};
