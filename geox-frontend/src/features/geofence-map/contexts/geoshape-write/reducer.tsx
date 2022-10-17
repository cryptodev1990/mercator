import { GeoShape } from "../../../../client";
import { Action } from "./action-types";

export type UndoLogRecord = {
  op:
    | "ADD_SHAPE"
    | "DELETE_SHAPES"
    | "UPDATE_SHAPE"
    | "BULK_ADD_SHAPES"
    | "BULK_ADD_SHAPE_SPLIT";
  payload: any;
};

export interface State {
  shapeUpdateLoading: boolean;
  shapeAddLoading: boolean;
  tileCacheKey: number;
  undoLog: UndoLogRecord[];
  redoLog: UndoLogRecord[];
  updatedShapeIds: string[];
  updatedShape: GeoShape | null;
  updateError: Error | null;
}

export const initialState: State = {
  shapeUpdateLoading: false,
  shapeAddLoading: false,
  tileCacheKey: 0,
  undoLog: [],
  redoLog: [],
  updatedShapeIds: [],
  updatedShape: null,
  updateError: null,
};

export function reducer(state: State, action: Action): State {
  switch (action.type) {
    // Shape metadata actions
    // Add shape actions
    case "BULK_ADD_SHAPES_LOADING":
    case "ADD_SHAPE_LOADING":
    case "UPDATE_SHAPE_LOADING":
    case "DELETE_SHAPES_LOADING": {
      const res = {
        ...state,
        shapeUpdateLoading: true,
      };
      if (action.type === "ADD_SHAPE_LOADING") {
        res.shapeAddLoading = true;
      }
      return res;
    }
    case "DELETE_SHAPES_SUCCESS":
    case "BULK_ADD_SHAPES_SUCCESS": {
      return {
        ...state,
        shapeUpdateLoading: false,
        tileCacheKey: state.tileCacheKey + 1,
        updatedShapeIds: action.updatedShapeIds || [],
      };
    }
    case "ADD_SHAPE_SUCCESS":
    case "UPDATE_SHAPE_SUCCESS": {
      return {
        ...state,
        shapeUpdateLoading: false,
        shapeAddLoading: false,
        tileCacheKey: state.tileCacheKey + 1,
        updatedShapeIds: action.updatedShapeIds || [],
        updatedShape: action?.updatedShape ?? null,
      };
    }
    case "BULK_ADD_SHAPES_ERROR":
    case "ADD_SHAPE_ERROR":
    case "DELETE_SHAPES_ERROR":
    case "UPDATE_SHAPE_ERROR": {
      return {
        ...state,
        updateError: action.error,
        shapeUpdateLoading: false,
        shapeAddLoading: false,
      };
    }
    default:
      return state;
  }
}
