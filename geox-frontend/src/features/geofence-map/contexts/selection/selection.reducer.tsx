import { Feature } from "@turf/helpers";
import _ from "lodash";
import { Action } from "./actions";

export interface State {
  selectedShapes: Feature[];
}

export const initialState = {
  selectedShapes: [],
};

export function selectionReducer(state: State, action: Action): State {
  switch (action.type) {
    case "ADD_SHAPES_TO_SELECTED_SHAPES": {
      const distinctShapes = _.uniqBy(
        [...state.selectedShapes, ...action.selectedShapes],
        "properties.__uuid"
      );

      return {
        ...state,
        selectedShapes: distinctShapes,
      };
    }

    case "REMOVE_SHAPE_FROM_SELECTED_SHAPES": {
      const selectedShapes = state.selectedShapes.filter(
        (shape: Feature) =>
          shape.properties && shape.properties.__uuid !== action.shapesUuids
      );
      return {
        ...state,
        selectedShapes,
      };
    }

    case "RESET_SELECTION": {
      return initialState;
    }
    default:
      return state;
  }
}
