import { Feature, FeatureCollection } from "@turf/helpers";
import {
  createContext,
  Dispatch,
  useContext,
  useEffect,
  useReducer,
} from "react";
import { GeoShapeMetadataContext } from "../geoshape-metadata/context";
import { selectionReducer, initialState, State } from "./selection.reducer";
import { Action } from "./actions";

export interface SelectionContextI {
  selectedShapes: Feature[];
  dispatch: Dispatch<Action>;
}

// We only need selectedShapes in our
export const SelectionContext = createContext<SelectionContextI>({
  selectedShapes: [],
  dispatch: () => {},
});

SelectionContext.displayName = "SelectionContext";

export const SelectionContextProvider = ({ children }: { children: any }) => {
  const [state, dispatch]: [State, Dispatch<Action>] = useReducer(
    selectionReducer,
    initialState
  );

  return (
    <SelectionContext.Provider
      value={{
        selectedShapes: state.selectedShapes,
        dispatch,
      }}
    >
      {children}
    </SelectionContext.Provider>
  );
};
