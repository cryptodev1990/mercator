import { GeoShape, GeoShapeCreate } from "../../../../client";
import { Action } from "./actions";

// get a type for an object that implements created_at and updated_at
export type OptionallyTimestamped = {
  uuid?: string;
  created_at?: string;
  updated_at?: string;
};

// deduplicate a list if OptionallyTimestamped objects based on a key
export function deduplicateShapes<T extends OptionallyTimestamped>(
  list: GeoShape[]
): GeoShape[] {
  const seen: any = {};
  for (const item of list) {
    if (!item.uuid) {
      continue;
    }
    const uuid = item.uuid;
    // If we've seen the item, prefer the latest version of it
    if (seen[uuid] && item.updated_at) {
      if (seen[uuid].updated_at < item?.updated_at) {
        seen[uuid] = item;
      }
      continue;
    }
    // If we haven't seen the item, add it to the list
    seen[uuid] = item;
  }
  return Object.values(seen);
}

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
  loading: boolean;
  optimisticShapeUpdates: GeoShape[] | GeoShapeCreate[];
  updatedShape: GeoShape | null;
  deletedShapeIds: string[];
  // TODO: all the states below should be removed
  updatedShapeIds: string[];
}

export const initialState: State = {
  loading: false,
  updatedShapeIds: [],
  updatedShape: null,
  deletedShapeIds: [],
  optimisticShapeUpdates: [],
};

export function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "SET_LOADING": {
      return {
        ...state,
        loading: action.value,
      };
    }
    case "SET_OPTIMISTIC_SHAPE": {
      const osu = state.optimisticShapeUpdates.map((shape) =>
        shape.uuid === action.shape.uuid ? action.shape : shape
      );
      return {
        ...state,
        updatedShapeIds: osu.map((shape: any) => shape.uuid),
        optimisticShapeUpdates: osu,
      };
    }
    case "DELETE_SHAPES_LOADING": {
      const osu = (state.optimisticShapeUpdates as GeoShape[]).filter(
        (s: GeoShape) => !action.deletedShapeIds.includes(s.uuid)
      );
      const res = {
        ...state,
        deletedShapeIds: [...state.deletedShapeIds, ...action.deletedShapeIds],
        optimisticShapeUpdates: osu,
      };
      return res;
    }
    case "BULK_ADD_SHAPES_LOADING": {
      const res = {
        ...state,
        loading: true,
        optimisticShapeUpdates: [
          ...state.optimisticShapeUpdates,
          ...action.updatedShapes,
        ],
      };
      return res;
    }
    case "ADD_SHAPE_LOADING": {
      const osu = [...new Set([...state.optimisticShapeUpdates, action.shape])];
      const res = {
        ...state,
        loading: true,
        optimisticShapeUpdates: osu,
      };
      return res;
    }
    case "BULK_ADD_SHAPES_SUCCESS": {
      const updatedShapeIds = [
        ...new Set([...state.updatedShapeIds, ...action.updatedShapeIds]),
      ];
      return {
        ...state,
        loading: false,
        updatedShapeIds,
      };
    }
    case "ADD_SHAPE_SUCCESS": {
      // TODO there are duplicates here, I'm not sure why
      // all these shapes arrive from the server, so they should be GeoShapes
      const osu = [
        ...state.optimisticShapeUpdates,
        action.updatedShape,
      ] as GeoShape[];
      const osuDeduped = deduplicateShapes(osu);
      // Sync with server updates

      return {
        ...state,
        loading: false,
        optimisticShapeUpdates: osuDeduped,
        updatedShape: action?.updatedShape ?? null,
        updatedShapeIds: [
          ...new Set([...state.updatedShapeIds, ...action.updatedShapeIds]),
        ],
      };
    }

    case "CLEAR_OPTIMISTIC_SHAPE_UPDATES": {
      return {
        ...state,
        optimisticShapeUpdates: [],
        deletedShapeIds: [],
        updatedShapeIds: [],
        loading: false,
      };
    }
    default:
      return state;
  }
}
