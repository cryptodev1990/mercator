import { difference } from "@turf/turf";
import { createContext, Dispatch, useContext, useReducer } from "react";
import { UseMutateFunction } from "react-query";
import {
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
  tileCacheKey: number;
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
    ShapeCountResponse,
    unknown,
    GeoShapeCreate[],
    unknown
  >;
  addShapeAndEdit: any;
  updateLoading: boolean;
  updatedShapeIds: string[];
  updatedShape: GeoShape | null;
}

export const GeoShapeWriteContext = createContext<IGeoShapeWriteContext>({
  tileCacheKey: 0,
  deleteShapes: async () => {},
  updateShape: async () => {},
  addShape: async () => {},
  bulkAddShapes: async () => {},
  bulkAddFromSplit: async () => {},
  updateLoading: false,
  addShapeAndEdit: async () => {},
  updatedShapeIds: [],
  updatedShape: null,
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
  const { deckRef } = useContext(DeckContext);

  function opLog(op: UndoLogRecord["op"], payload: any) {
    dispatch({
      type: "OP_LOG_ADD",
      op,
      payload,
    });
  }

  function bulkAddShapes(shapes: GeoShapeCreate[], ...args: any[]) {
    opLog("BULK_ADD_SHAPES", shapes);
    return api.bulkAddShapesApi(shapes, ...args);
  }

  function bulkAddFromSplit(
    shapes: GeoShapeCreate[],
    { onSuccess, onError }: any
  ) {
    opLog("BULK_ADD_SHAPE_SPLIT", shapes);
    return api.bulkAddShapesApi(shapes, {
      onSuccess,
      onError,
    });
  }

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
        .find((x: any) => x.id === "geofence-mvt");
      // TODO this produces way more features than it needs to, what gives?
      const currentFeatures = mvtLayer.getRenderedFeatures();
      for (const feat of currentFeatures) {
        const diffShape = difference(shape.geojson as any, feat);
        if (diffShape === null) {
          shape.geojson = {
            type: "Feature",
            geometry: {
              type: "Polygon",
              coordinates: [],
            },
          };
        }
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
    dispatch({ type: "DELETE_SHAPES_LOADING", uuids: shapeIds });
    return api.deleteShapesApi(shapeIds, ...args);
  }

  function updateShape(update: GeoShapeUpdate, params: any) {
    opLog("UPDATE_SHAPE", update);
    return api.updateShapeApi(update, params);
  }

  return (
    <GeoShapeWriteContext.Provider
      value={{
        updateLoading: state.shapeAddLoading || state.shapeUpdateLoading,
        tileCacheKey: state.tileCacheKey,
        addShape,
        deleteShapes,
        updateShape,
        bulkAddShapes,
        bulkAddFromSplit,
        addShapeAndEdit,
        updatedShapeIds: state.updatedShapeIds,
        updatedShape: state.updatedShape,
      }}
    >
      {children}
    </GeoShapeWriteContext.Provider>
  );
};
