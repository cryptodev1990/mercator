import { GeoShapeMetadata } from "../../../../client";

export interface State {
  uuids: GeoShapeMetadata["uuid"][];
  numSelected: number;
  isEmpty: boolean;
}

export const initialState = {
  uuids: [],
  numSelected: 0,
  isEmpty: false,
};

type Action =
  | {
      type: "ADD_SELECTED_SHAPE_UUIDS";
      uuids: GeoShapeMetadata["uuid"][];
    }
  | {
      type: "REMOVE_SELECTED_SHAPE_UUIDS";
      uuids: GeoShapeMetadata["uuid"][];
    }
  | { type: "RESET_SELECTION" };

export function selectionReducer(state: State, action: Action): State {
  switch (action.type) {
    case "ADD_SELECTED_SHAPE_UUIDS": {
      return generateFinalState(state, [...state.uuids, ...action.uuids]);
    }
    case "REMOVE_SELECTED_SHAPE_UUIDS": {
      return generateFinalState(
        state,
        state.uuids.filter((uuid) => !action.uuids.includes(uuid))
      );
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
