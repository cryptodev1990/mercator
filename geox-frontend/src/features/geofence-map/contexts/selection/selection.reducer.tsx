import { GeoShapeMetadata } from "../../../../client";

export interface State {
  uuids: GeoShapeMetadata["uuid"][];
  multiSelectedUuids: GeoShapeMetadata["uuid"][];
  numSelected: number;
  isEmpty: boolean;
}

export const initialState = {
  uuids: [],
  multiSelectedUuids: [],
  numSelected: 0,
  isEmpty: false,
};

type Action =
  | {
      type: "ADD_SELECTED_SHAPE_UUIDS";
      uuids: GeoShapeMetadata["uuid"][];
    }
  | {
      type: "ADD_SHAPE_TO_MULTISELECT";
      multiSelectedUuid: GeoShapeMetadata["uuid"];
    }
  | {
      type: "REMOVE_SHAPE_FROM_MULTISELECT";
      multiSelectedUuid: GeoShapeMetadata["uuid"];
    }
  | {
      type: "REMOVE_SELECTED_SHAPE_UUIDS";
      uuids: GeoShapeMetadata["uuid"][];
    }
  | {
      type: "CLEAR_MULTI_SELECTED_SHAPE_UUIDS";
    }
  | { type: "RESET_SELECTION" };

export function selectionReducer(state: State, action: Action): State {
  switch (action.type) {
    case "ADD_SELECTED_SHAPE_UUIDS": {
      return generateFinalState(state, [...state.uuids, ...action.uuids]);
    }
    case "ADD_SHAPE_TO_MULTISELECT": {
      return {
        ...state,
        multiSelectedUuids: [
          ...state.multiSelectedUuids,
          action.multiSelectedUuid,
        ],
      };
    }
    case "REMOVE_SHAPE_FROM_MULTISELECT": {
      const multiSelectedUuids = state.multiSelectedUuids.filter(
        (uuid) => uuid !== action.multiSelectedUuid
      );
      return {
        ...state,
        multiSelectedUuids,
      };
    }
    case "REMOVE_SELECTED_SHAPE_UUIDS": {
      return generateFinalState(
        state,
        state.uuids.filter((uuid) => !action.uuids.includes(uuid))
      );
    }
    case "CLEAR_MULTI_SELECTED_SHAPE_UUIDS": {
      return {
        ...state,
        multiSelectedUuids: [],
      };
    }
    case "RESET_SELECTION": {
      return initialState;
    }
    default:
      return state;
  }
}

const generateFinalState = (
  state: State,
  uuids: GeoShapeMetadata["uuid"][]
) => {
  return {
    ...state,
    uuids,
    numSelected: uuids.length,
    isEmpty: uuids.length === 0,
  };
};
