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
      type: "ADD_MULTI_SELECTED_SHAPE_UUIDS";
      multiSelectedUuids: GeoShapeMetadata["uuid"][];
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
    case "ADD_MULTI_SELECTED_SHAPE_UUIDS": {
      console.log("add multiselect shape", [
        ...state.multiSelectedUuids,
        ...action.multiSelectedUuids,
      ]);
      return {
        ...state,
        multiSelectedUuids: [
          ...state.multiSelectedUuids,
          ...action.multiSelectedUuids,
        ],
      };
    }
    case "REMOVE_SELECTED_SHAPE_UUIDS": {
      return generateFinalState(
        state,
        state.uuids.filter((uuid) => !action.uuids.includes(uuid))
      );
    }
    case "RESET_SELECTION": {
      console.log("I am resetting");
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
