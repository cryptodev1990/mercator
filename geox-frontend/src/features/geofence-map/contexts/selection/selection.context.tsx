import { FeatureCollection } from "@turf/helpers";
import { createContext, useContext, useEffect, useReducer } from "react";
import { GeoShapeMetadata } from "../../../../client/models/GeoShapeMetadata";
import { useGetOneShapeByUuid } from "../../hooks/use-openapi-hooks";
import { geoShapesToFeatureCollection } from "../../utils";
import { GeoShapeMetadataContext } from "../geoshape-metadata/context";
import { selectionReducer, initialState } from "./selection.reducer";

export interface SelectionContextI {
  selectedUuids: GeoShapeMetadata["uuid"][];
  isSelected: (shape: GeoShapeMetadata | string) => boolean;
  addSelectedShapeUuid: (uuid: string) => void;
  selectOneShapeUuid: (uuid: string) => void;
  removeSelectedShapeUuid: (uuid: string) => void;
  clearSelectedShapeUuids: () => void;
  selectedFeatureCollection: FeatureCollection | null;
  selectedDataIsLoading: boolean;
  numSelected: number;
}

export const SelectionContext = createContext<SelectionContextI>({
  selectedUuids: [],
  isSelected: () => false,
  addSelectedShapeUuid: () => {},
  selectOneShapeUuid: () => {},
  removeSelectedShapeUuid: () => {},
  clearSelectedShapeUuids: () => {},
  selectedFeatureCollection: null,
  selectedDataIsLoading: false,
  numSelected: 0,
});

SelectionContext.displayName = "SelectionContext";

export const SelectionContextProvider = ({ children }: { children: any }) => {
  const [state, dispatch] = useReducer(selectionReducer, initialState);

  // TODO create a bulk query for this
  const { data: selectedShapeData, isLoading: selectedDataIsLoading } =
    useGetOneShapeByUuid(state.uuids[0] ?? null);

  const addSelectedShapeUuid = (uuid: string) => {
    dispatch({ type: "ADD_SELECTED_SHAPE_UUIDS", uuids: [uuid] });
  };

  const selectOneShapeUuid = (uuid: string) => {
    dispatch({ type: "RESET_SELECTION" });
    dispatch({ type: "ADD_SELECTED_SHAPE_UUIDS", uuids: [uuid] });
  };

  const removeSelectedShapeUuid = (uuid: string) => {
    dispatch({ type: "REMOVE_SELECTED_SHAPE_UUIDS", uuids: [uuid] });
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
        numSelected: state.numSelected,
        isSelected,
        addSelectedShapeUuid,
        selectOneShapeUuid,
        removeSelectedShapeUuid,
        clearSelectedShapeUuids,
        // @ts-ignore
        selectedFeatureCollection,
        selectedDataIsLoading,
      }}
    >
      {children}
    </SelectionContext.Provider>
  );
};
