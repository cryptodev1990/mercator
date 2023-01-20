import { Feature, FeatureCollection } from "@turf/helpers";
import { GeoShapeMetadata } from "../../../../client";
import _ from "lodash";

export interface State {
  selectedShapesUuids: GeoShapeMetadata["uuid"][];
  selectedShapes: Feature[];
  numSelected: number;
  isEmpty: boolean;
}

export const initialState = {
  selectedShapesUuids: [],
  selectedShapes: [],
  numSelected: 0,
  isEmpty: false,
};

type Action =
  | {
      type: "ADD_SELECTED_SHAPE_UUIDS";
      selectedShapesUuids: GeoShapeMetadata["uuid"][];
    }
  | {
      type: "ADD_SHAPES_TO_SELECTED_SHAPES";
      selectedShapes: Feature[];
    }
  | {
      type: "REMOVE_SHAPE_FROM_SELECTED_SHAPES";
      multiSelectedUuid: GeoShapeMetadata["uuid"];
    }
  | { type: "RESET_SELECTION" };

export function selectionReducer(state: State, action: Action): State {
  switch (action.type) {
    case "ADD_SELECTED_SHAPE_UUIDS": {
      return generateFinalState(state, [
        ...state.selectedShapesUuids,
        ...action.selectedShapesUuids,
      ]);
    }

    case "ADD_SHAPES_TO_SELECTED_SHAPES": {
      const distinctShapes = _.uniqBy(
        [...state.selectedShapes, ...action.selectedShapes],
        "properties.__uuid"
      );

      return {
        ...state,
        selectedShapesUuids: [
          ...state.selectedShapesUuids,
          ...distinctShapes.map(
            (shape: Feature) => shape.properties && shape.properties.__uuid
          ),
        ],
        selectedShapes: distinctShapes,
      };
    }

    case "REMOVE_SHAPE_FROM_SELECTED_SHAPES": {
      const selectedShapesUuids = state.selectedShapesUuids.filter(
        (uuid) => uuid !== action.multiSelectedUuid
      );
      const selectedShapes = state.selectedShapes.filter(
        (shape: Feature) =>
          shape.properties &&
          shape.properties.__uuid !== action.multiSelectedUuid
      );
      return {
        ...state,
        selectedShapesUuids,
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

const generateFinalState = (
  state: State,
  selectedShapesUuids: GeoShapeMetadata["uuid"][]
) => {
  return {
    ...state,
    selectedShapesUuids,
    numSelected: selectedShapesUuids.length,
    isEmpty: selectedShapesUuids.length === 0,
  };
};
