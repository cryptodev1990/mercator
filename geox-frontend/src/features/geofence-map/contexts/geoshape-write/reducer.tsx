import { GeoShape, GeoShapeCreate } from "../../../../client";
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
  optimisticShapeUpdates: GeoShapeCreate[];
  tileCacheKey: number;
  undoLog: UndoLogRecord[];
  redoLog: UndoLogRecord[];
  updatedShapeIds: string[];
  updatedShape: GeoShape | null;
  updateError: Error | null;
  deletedShapeIds: string[];
}

export const initialState: State = {
  shapeUpdateLoading: false,
  shapeAddLoading: false,
  tileCacheKey: 0,
  optimisticShapeUpdates: [],
  undoLog: [],
  redoLog: [],
  updatedShapeIds: [],
  updatedShape: null,
  updateError: null,
  deletedShapeIds: [],
};

export function reducer(state: State, action: Action): State {
  switch (action.type) {
    // Shape metadata actions
    // Add shape actions
    case "UPDATE_SHAPE_LOADING":
    case "DELETE_SHAPES_LOADING": {
      const res = {
        ...state,
        shapeUpdateLoading: true,
      };
      return res;
    }
    case "BULK_ADD_SHAPES_LOADING": {
      const res = {
        ...state,
        shapeUpdateLoading: true,
        shapeAddLoading: true,
      };
      return res;
    }
    case "ADD_SHAPE_LOADING": {
      const optimisticShapeUpdates = [action.shape];
      for (const shape of state.optimisticShapeUpdates) {
        optimisticShapeUpdates.push(shape);
      }
      const res = {
        ...state,
        shapeUpdateLoading: true,
        shapeAddLoading: true,
        optimisticShapeUpdates,
      };
      return res;
    }
    case "DELETE_SHAPES_SUCCESS":
    case "BULK_ADD_SHAPES_SUCCESS": {
      return {
        ...state,
        shapeUpdateLoading: false,
        tileCacheKey: state.tileCacheKey + 1,
        updatedShapeIds: action.updatedShapeIds || [],
        deletedShapeIds:
          action.type === "DELETE_SHAPES_SUCCESS" ? action.updatedShapeIds : [],
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
    case "CLEAR_OPTIMISTIC_SHAPE_UPDATES": {
      return {
        ...state,
        optimisticShapeUpdates: [],
      };
    }
    default:
      return state;
  }
}
