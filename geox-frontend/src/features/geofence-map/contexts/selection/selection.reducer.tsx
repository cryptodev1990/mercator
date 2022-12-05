import { Feature, FeatureCollection } from "@turf/helpers";
import { GeoShapeMetadata } from "../../../../client";
import _ from "lodash";

export interface State {
  uuids: GeoShapeMetadata["uuid"][];
  multiSelectedShapesUuids: GeoShapeMetadata["uuid"][];
  multiSelectedShapes: Feature[];
  numSelected: number;
  isEmpty: boolean;
}

export const initialState = {
  uuids: [],
  multiSelectedShapesUuids: [],
  multiSelectedShapes: [],
  numSelected: 0,
  isEmpty: false,
};

type Action =
  | {
      type: "ADD_SELECTED_SHAPE_UUIDS";
      uuids: GeoShapeMetadata["uuid"][];
    }
  | {
      type: "ADD_SHAPES_TO_MULTISELECTED_SHAPES";
      multiSelectedShapes: Feature[];
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

    case "ADD_SHAPES_TO_MULTISELECTED_SHAPES": {
      const distinctShapes = _.uniqBy(
        [...state.multiSelectedShapes, ...action.multiSelectedShapes],
        "properties.__uuid"
      );

      return {
        ...state,
        multiSelectedShapesUuids: distinctShapes.map(
          (shape: Feature) => shape.properties && shape.properties.__uuid
        ),
        multiSelectedShapes: distinctShapes,
      };
    }

    case "REMOVE_SHAPE_FROM_MULTISELECT": {
      const multiSelectedShapesUuids = state.multiSelectedShapesUuids.filter(
        (uuid) => uuid !== action.multiSelectedUuid
      );
      const multiSelectedShapes = state.multiSelectedShapes.filter(
        (shape: Feature) =>
          shape.properties &&
          shape.properties.__uuid !== action.multiSelectedUuid
      );
      return {
        ...state,
        multiSelectedShapesUuids,
        multiSelectedShapes,
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
        multiSelectedShapesUuids: [],
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
