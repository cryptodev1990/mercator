import { difference } from "@turf/turf";
import {
  createContext,
  Dispatch,
  useContext,
  useEffect,
  useMemo,
  useReducer,
} from "react";
import { UseMutateFunction, useQueryClient } from "react-query";
import {
  GeofencerService,
  GeoShape,
  GeoShapeCreate,
  GeoShapeMetadata,
  GeoShapeUpdate,
  ShapeCountResponse,
} from "../../../../client";
import { aggressiveLog } from "../../../../common/aggressive-log";
import { useCursorMode } from "../../hooks/use-cursor-mode";
import { DeckContext } from "../deck-context";
import { Action } from "./action-types";
import { useApi } from "./api.hook";
import { reducer, initialState, State, UndoLogRecord } from "./reducer";

export interface IGeoShapeWriteContext {
  // Refreshes the shape tiles
  // API call - bulk delete
  deleteShapes: UseMutateFunction<
    ShapeCountResponse,
    unknown,
    string[],
    unknown
  >;
  // API call - update shape
  updateShape: UseMutateFunction<
    GeoShapeMetadata,
    unknown,
    GeoShapeUpdate,
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
    GeoShapeCreate[],
    unknown
  >;
  bulkAddFromSplit: UseMutateFunction<
    GeoShapeCreate[],
    unknown,
    GeoShapeCreate[],
    unknown
  >;
  addShapeAndEdit: any;
  updateLoading: boolean;
  updatedShapeIds: string[];
  deletedShapeIds: string[];
  updatedShape: GeoShape | null;
  partialUpdateShape: (shape: GeoShapeUpdate) => void;
  optimisticShapeUpdates: GeoShapeCreate[];
  clearOptimisticShapeUpdates: () => void;
  deletedShapeIdSet: Set<string>;
  updatedShapeIdSet: Set<string>;
}

export const GeoShapeWriteContext = createContext<IGeoShapeWriteContext>({
  deleteShapes: async () => {},
  updateShape: async () => {},
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
  partialUpdateShape: async () => {},
  deletedShapeIdSet: new Set(),
  updatedShapeIdSet: new Set(),
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

  function opLog(op: UndoLogRecord["op"], payload: any) {
    dispatch({
      type: "OP_LOG_ADD",
      op,
      payload,
    });
  }

  function bulkAddShapes(shapes: GeoShapeCreate[], ...args: any[]) {
    opLog("BULK_ADD_SHAPES", shapes);
    api.setPreferList(false);
    return api.bulkAddShapesApi(shapes, ...args);
  }

  useEffect(() => {
    setHoveredUuid(null);
  }, [state.deletedShapeIds]);

  function bulkAddFromSplit(
    shapes: GeoShapeCreate[],
    { onSuccess, onError }: any
  ) {
    opLog("BULK_ADD_SHAPE_SPLIT", shapes);
    api.setPreferList(true);
    return api.bulkAddShapesApi(shapes, {
      onSuccess,
      onError,
    });
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
    opLog("ADD_SHAPE", shape);
    dispatch({ type: "ADD_SHAPE_LOADING", shape });
    return api.addShapeApi(removeOverlapFrom(shape), ...args);
  }

  const addShapeAndEdit = async (
    shape: GeoShapeCreate,
    onSuccess: (x: GeoShapeMetadata) => void
  ) => {
    opLog("ADD_SHAPE", shape);
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
    opLog("DELETE_SHAPES", shapeIds);
    return api.deleteShapesApi(shapeIds, ...args);
  }

  function updateShape(update: GeoShapeUpdate, params: any) {
    opLog("UPDATE_SHAPE", update);
    dispatch({ type: "UPDATE_SHAPE_LOADING", shapes: [update as GeoShape] });
    return api.updateShapeApi(update, params);
  }

  const qc = useQueryClient();
  function partialUpdateShape(update: GeoShapeUpdate) {
    if (!update.uuid) {
      throw new Error("update must have a uuid");
    }
    opLog("UPDATE_SHAPE", update);
    // @ts-ignore
    dispatch({ type: "UPDATE_PARTIAL_SHAPE", shapes: [update] });

    GeofencerService.patchShapesShapeIdGeofencerShapesShapeIdPatch(
      update.uuid,
      update
    ).then((data: GeoShape) => {
      dispatch({
        type: "UPDATE_SHAPE_SUCCESS",
        updatedShapeIds: [data.uuid],
        updatedShape: data,
      });
      qc.fetchQuery("geofencer");
    });
  }

  function clearOptimisticShapeUpdates() {
    dispatch({ type: "CLEAR_OPTIMISTIC_SHAPE_UPDATES" });
  }

  return (
    <GeoShapeWriteContext.Provider
      value={{
        updateLoading: state.shapeAddLoading || state.shapeUpdateLoading,
        addShape,
        deleteShapes,
        updateShape,
        bulkAddShapes,
        bulkAddFromSplit,
        addShapeAndEdit,
        partialUpdateShape,
        optimisticShapeUpdates: state.optimisticShapeUpdates,
        updatedShapeIds: state.updatedShapeIds,
        updatedShape: state.updatedShape,
        deletedShapeIds: state.deletedShapeIds,
        clearOptimisticShapeUpdates,
        deletedShapeIdSet,
        updatedShapeIdSet,
      }}
    >
      {children}
    </GeoShapeWriteContext.Provider>
  );
};
