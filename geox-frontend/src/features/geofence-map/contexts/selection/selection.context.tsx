import { FeatureCollection } from "@turf/helpers";
import { createContext, useContext, useEffect, useReducer } from "react";
import { GeoShape, GeoShapeCreate } from "../../../../client";
import { GeoShapeMetadata } from "../../../../client/models/GeoShapeMetadata";
import {
  useGetOneShapeByUuid,
  useGetShapesByUuids,
} from "../../hooks/use-openapi-hooks";
import { geoShapesToFeatureCollection } from "../../utils";
import { GeoShapeMetadataContext } from "../geoshape-metadata/context";
import { selectionReducer, initialState } from "./selection.reducer";

export interface SelectionContextI {
  selectedUuids: GeoShapeMetadata["uuid"][];
  setSelectedShapeUuid: (uuid: string) => void;
  multiSelectedUuids: GeoShapeMetadata["uuid"][];
  setMultiSelectedShapeUuids: (uuids: string) => void;
  isSelected: (shape: GeoShapeMetadata | string) => boolean;
  removeSelectedShapeUuid: (uuid: string) => void;
  clearMultiSelectedShapeUuids: () => void;
  clearSelectedShapeUuids: () => void;
  selectedFeatureCollection: FeatureCollection | null;
  multiSelectedFeatureCollection: any | null;
  selectedDataIsLoading: boolean;
  numSelected: number;
}

export const SelectionContext = createContext<SelectionContextI>({
  selectedUuids: [],
  setSelectedShapeUuid: () => {},
  multiSelectedUuids: [],
  setMultiSelectedShapeUuids: () => {},
  isSelected: () => false,
  removeSelectedShapeUuid: () => {},
  clearMultiSelectedShapeUuids: () => {},
  clearSelectedShapeUuids: () => {},
  selectedFeatureCollection: null,
  multiSelectedFeatureCollection: null,
  selectedDataIsLoading: false,
  numSelected: 0,
});

SelectionContext.displayName = "SelectionContext";

export const SelectionContextProvider = ({ children }: { children: any }) => {
  const [state, dispatch] = useReducer(selectionReducer, initialState);

  // TODO create a bulk query for this
  const { data: selectedShapeData, isLoading: selectedDataIsLoading } =
    useGetOneShapeByUuid(state.uuids[0] ?? null);

  const setSelectedShapeUuid = (uuid: string) => {
    dispatch({ type: "RESET_SELECTION" });
    dispatch({ type: "ADD_SELECTED_SHAPE_UUIDS", uuids: [uuid] });
  };

  const setMultiSelectedShapeUuids = (uuid: string) => {
    dispatch({
      type: "ADD_MULTI_SELECTED_SHAPE_UUIDS",
      multiSelectedUuids: [uuid],
    });
  };

  const removeSelectedShapeUuid = (uuid: string) => {
    dispatch({ type: "REMOVE_SELECTED_SHAPE_UUIDS", uuids: [uuid] });
  };

  const clearMultiSelectedShapeUuids = () => {
    dispatch({
      type: "CLEAR_MULTI_SELECTED_SHAPE_UUIDS",
    });
  };

  const clearSelectedShapeUuids = () => {
    dispatch({ type: "RESET_SELECTION" });
  };

  const isSelected = (
    shapeOrUuid: GeoShapeMetadata | string | undefined
  ): boolean => {
    if (!shapeOrUuid) return false;
    if (typeof shapeOrUuid === "string") {
      return state.uuids.includes(shapeOrUuid);
    }
    return state.uuids.includes(shapeOrUuid.uuid ?? null);
  };
  const selectedFeatureCollection = geoShapesToFeatureCollection(
    selectedShapeData ? [selectedShapeData] : []
  );

  const multiselectedShapeData = useGetShapesByUuids(
    state.multiSelectedUuids ?? null
  );

  const multiSelectedFeatureCollection = geoShapesToFeatureCollection(
    multiselectedShapeData ? multiselectedShapeData : []
  );
  console.log("multi", multiselectedShapeData);
  // remove selection if the visible shapes change
  const { visibleNamespaces, activeNamespaces } = useContext(
    GeoShapeMetadataContext
  );
  useEffect(() => {
    dispatch({ type: "RESET_SELECTION" });
  }, [visibleNamespaces, activeNamespaces]);

  return (
    <SelectionContext.Provider
      value={{
        selectedUuids: state.uuids,
        multiSelectedUuids: state.multiSelectedUuids,
        numSelected: state.numSelected,
        isSelected,
        setSelectedShapeUuid,
        setMultiSelectedShapeUuids,
        removeSelectedShapeUuid,
        clearMultiSelectedShapeUuids,
        clearSelectedShapeUuids,
        // @ts-ignore
        selectedFeatureCollection,
        multiSelectedFeatureCollection,
        selectedDataIsLoading,
      }}
    >
      {children}
    </SelectionContext.Provider>
  );
};
