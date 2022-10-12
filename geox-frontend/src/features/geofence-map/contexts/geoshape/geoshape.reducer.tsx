import { GeoShapeMetadata } from "../../../../client";

type UndoLogRecord = {
  op:
    | "ADD_SHAPE"
    | "DELETE_SHAPES"
    | "UPDATE_SHAPE"
    | "BULK_ADD_SHAPES"
    | "BULK_ADD_SHAPE_SPLIT";
  payload: any;
};

export interface State {
  shapeMetadata: GeoShapeMetadata[];
  shapeMetadataIsLoading: boolean;
  shapeMetadataError: Error | null;
  numShapes: number | null;
  numShapesIsLoading: boolean;
  numShapesError: Error | null;
  updateError: Error | null;
  shapeUpdateLoading: boolean;
  tileCacheKey: number;
  undoLog: UndoLogRecord[];
  redoLog: UndoLogRecord[];
}

export const initialState: State = {
  shapeMetadata: [],
  shapeMetadataIsLoading: false,
  shapeMetadataError: null,
  numShapes: null,
  numShapesIsLoading: false,
  numShapesError: null,
  shapeUpdateLoading: false,
  updateError: null,
  tileCacheKey: 0,
  undoLog: [],
  redoLog: [],
};

type Action =
  | {
      type: "FETCH_SHAPE_METADATA_LOADING";
    }
  | {
      type: "FETCH_SHAPE_METADATA_SUCCESS";
      shapeMetdata: GeoShapeMetadata[];
    }
  | {
      type: "FETCH_SHAPE_METADATA_ERROR";
      error: Error;
    }
  | {
      type: "FETCH_NUM_SHAPES_LOADING";
    }
  | {
      type: "FETCH_NUM_SHAPES_SUCCESS";
      numShapes: number;
    }
  | {
      type: "FETCH_NUM_SHAPES_ERROR";
      error: Error;
    }
  | {
      type: "ADD_SHAPE_LOADING";
      shape: GeoShapeMetadata;
    }
  | {
      type: "ADD_SHAPE_SUCCESS";
    }
  | {
      type: "ADD_SHAPE_ERROR";
      error: Error;
    }
  | {
      type: "DELETE_SHAPES_LOADING";
      uuid: string;
    }
  | {
      type: "DELETE_SHAPES_SUCCESS";
      uuid: string;
    }
  | {
      type: "DELETE_SHAPES_ERROR";
      error: Error;
    }
  | {
      type: "UPDATE_SHAPE_LOADING";
      shape: GeoShapeMetadata;
    }
  | {
      type: "UPDATE_SHAPE_SUCCESS";
    }
  | {
      type: "UPDATE_SHAPE_ERROR";
      error: Error;
    }
  | {
      type: "BULK_ADD_SHAPES_LOADING";
    }
  | {
      type: "BULK_ADD_SHAPES_SUCCESS";
    }
  | {
      type: "BULK_ADD_SHAPES_ERROR";
      error: Error;
    }
  | {
      type: "OP_LOG_ADD";
      op:
        | "ADD_SHAPE"
        | "DELETE_SHAPES"
        | "UPDATE_SHAPE"
        | "BULK_ADD_SHAPES"
        | "BULK_ADD_SHAPE_SPLIT";
      payload: any;
    }
  | {
      type: "OP_LOG_UNDO" | "OP_LOG_REDO";
      op: any;
      payload: any;
    }
  | {
      type: "SNAPSHOT_START";
      selectedFeatureCollection: any;
    }
  | {
      type: "SNAPSHOT_END";
      selectedFeatureCollection: any;
    };

export function geoshapeReducer(state: State, action: Action): State {
  switch (action.type) {
    // Shape metadata actions
    case "FETCH_SHAPE_METADATA_LOADING": {
      return {
        ...state,
        shapeMetadataIsLoading: true,
      };
    }
    case "FETCH_SHAPE_METADATA_SUCCESS": {
      return {
        ...state,
        shapeMetadataIsLoading: false,
        shapeMetadata: action.shapeMetdata,
      };
    }
    case "FETCH_SHAPE_METADATA_ERROR": {
      return {
        ...state,
        shapeMetadataIsLoading: false,
        shapeMetadataError: action.error,
      };
    }
    // Shape count actions
    case "FETCH_NUM_SHAPES_LOADING": {
      return {
        ...state,
        numShapesIsLoading: true,
      };
    }
    case "FETCH_NUM_SHAPES_SUCCESS": {
      return {
        ...state,
        numShapesIsLoading: false,
        numShapes: action.numShapes,
      };
    }
    case "FETCH_NUM_SHAPES_ERROR": {
      return {
        ...state,
        shapeMetadataIsLoading: false,
        shapeMetadataError: action.error,
      };
    }
    case "OP_LOG_ADD": {
      // keep only last 20 operations
      const undoLog = state.undoLog.slice(-20);
      return {
        ...state,
        undoLog: [
          ...undoLog,
          {
            op: action.op,
            payload: action.payload,
          },
        ],
        redoLog: [],
      };
    }
    case "OP_LOG_UNDO": {
      if (state.undoLog.length === 0) {
        return state;
      }
      return {
        ...state,
        undoLog: state.undoLog.slice(0, -1),
        redoLog: [...state.redoLog, { op: action.op, payload: action.payload }],
      };
    }
    case "OP_LOG_REDO": {
      if (state.redoLog.length === 0) {
        return state;
      }
      return {
        ...state,
        redoLog: state.redoLog.slice(0, -1),
        undoLog: [...state.undoLog, { op: action.op, payload: action.payload }],
      };
    }
    // Add shape actions
    case "BULK_ADD_SHAPES_LOADING":
    case "ADD_SHAPE_LOADING":
    case "UPDATE_SHAPE_LOADING":
    case "DELETE_SHAPES_LOADING": {
      return {
        ...state,
        shapeUpdateLoading: true,
      };
    }
    case "BULK_ADD_SHAPES_SUCCESS":
    case "ADD_SHAPE_SUCCESS":
    case "UPDATE_SHAPE_SUCCESS":
    case "DELETE_SHAPES_SUCCESS": {
      return {
        ...state,
        shapeUpdateLoading: false,
        tileCacheKey: state.tileCacheKey + 1,
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
      };
    }
    default:
      return state;
  }
}
