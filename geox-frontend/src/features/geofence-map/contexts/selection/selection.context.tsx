import { Feature, FeatureCollection } from "@turf/helpers";
import { createContext, useContext, useEffect, useReducer } from "react";
import { GeoShapeMetadata } from "../../../../client/models/GeoShapeMetadata";
import { useGetOneShapeByUuid } from "../../hooks/use-openapi-hooks";
import { geoShapesToFeatureCollection } from "../../utils";
import { GeoShapeMetadataContext } from "../geoshape-metadata/context";
import { selectionReducer, initialState } from "./selection.reducer";

export interface SelectionContextI {
  selectedUuids: GeoShapeMetadata["uuid"][];
  setSelectedShapeUuid: (uuid: string) => void;
  selectedShapes: Feature[];
  addShapesToMultiSelectedShapes: (shape: Feature[]) => void;
  isSelected: (shape: GeoShapeMetadata | string) => boolean;
  removeShapeFromMultiSelectedShapes: (uuid: string) => void;
  clearSelectedShapeUuids: () => void;
  selectedFeatureCollection: FeatureCollection | null;
  selectedDataIsLoading: boolean;
  numSelected: number;
}

export const SelectionContext = createContext<SelectionContextI>({
  selectedUuids: [],
  setSelectedShapeUuid: () => {},
  selectedShapes: [],
  addShapesToMultiSelectedShapes: () => {},
  isSelected: () => false,
  removeShapeFromMultiSelectedShapes: () => {},
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
    useGetOneShapeByUuid(state.selectedShapesUuids[0] ?? null);

  const setSelectedShapeUuid = (uuid: string) => {
    dispatch({ type: "ADD_SELECTED_SHAPE_UUIDS", selectedShapesUuids: [uuid] });
  };

  const addShapesToMultiSelectedShapes = (shape: Feature[]) => {
    dispatch({
      type: "ADD_SHAPES_TO_SELECTED_SHAPES",
      selectedShapes: shape,
    });
  };

  const removeShapeFromMultiSelectedShapes = (uuid: string) => {
    dispatch({
      type: "REMOVE_SHAPE_FROM_SELECTED_SHAPES",
      multiSelectedUuid: uuid,
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
      return state.selectedShapesUuids.includes(shapeOrUuid);
    }
    return state.selectedShapesUuids.includes(shapeOrUuid.uuid ?? null);
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
        selectedUuids: state.selectedShapesUuids,
        selectedShapes: state.selectedShapes,
        numSelected: state.numSelected,
        isSelected,
        setSelectedShapeUuid,
        removeShapeFromMultiSelectedShapes,
        clearSelectedShapeUuids,
        addShapesToMultiSelectedShapes,
        // @ts-ignore
        selectedFeatureCollection,
        selectedDataIsLoading,
      }}
    >
      {children}
    </SelectionContext.Provider>
  );
};
