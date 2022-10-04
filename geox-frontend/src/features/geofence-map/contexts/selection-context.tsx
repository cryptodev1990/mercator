import { FeatureCollection } from "@turf/helpers";
import { createContext, useEffect, useState } from "react";
import { GeoShapeMetadata } from "../../../client/models/GeoShapeMetadata";
import { useGetOneShapeByUuid } from "../hooks/openapi-hooks";
import { geoShapesToFeatureCollection } from "../utils";

interface SelectionContextState {
  selectedShapeUuids: Record<string, boolean>;
  setSelectedShapeUuids: (selectedShapes: Record<string, boolean>) => void;
  isSelected: (shape: GeoShapeMetadata | string) => boolean;
  addSelectedShapeUuid: (uuid: string) => void;
  getNumSelectedShapes: () => number;
  selectOneShapeUuid: (uuid: string) => void;
  addManySelectedShapeUuids: (uuids: string[]) => void;
  removeSelectedShapeUuid: (uuid: string) => void;
  clearSelectedShapeUuids: () => void;
  selectedFeatureCollection: FeatureCollection | null;
  selectedDataIsLoading: boolean;
}

export const SelectionContext = createContext<SelectionContextState>({
  selectedShapeUuids: {},
  setSelectedShapeUuids: () => {},
  isSelected: () => false,
  addSelectedShapeUuid: () => {},
  getNumSelectedShapes: () => 0,
  selectOneShapeUuid: () => {},
  addManySelectedShapeUuids: () => {},
  removeSelectedShapeUuid: () => {},
  clearSelectedShapeUuids: () => {},
  selectedFeatureCollection: null,
  selectedDataIsLoading: false,
});

SelectionContext.displayName = "SelectionContext";

export const SelectionContextContainer = ({ children }: { children: any }) => {
  const [selectedShapeUuids, setSelectedShapeUuids] = useState<
    Record<string, boolean>
  >({});

  useEffect(() => {
    console.log("Selected", Object.keys(selectedShapeUuids)[0]);
  }, [selectedShapeUuids]);

  const selectedShapeUuid = Object.keys(selectedShapeUuids)[0];
  const { data: selectedShapeData, isLoading: selectedDataIsLoading } =
    useGetOneShapeByUuid(selectedShapeUuid);
  console.log("selectedShapeData", selectedShapeData);

  const addSelectedShapeUuid = (uuid: string) => {
    const output = { ...selectedShapeUuids };
    output[uuid] = true;
    setSelectedShapeUuids(output);
  };

  const getNumSelectedShapes = () => {
    return Object.keys(selectedShapeUuids).length;
  };

  const selectOneShapeUuid = (uuid: string) => {
    const res: Record<string, boolean> = {};
    res[uuid] = true;
    setSelectedShapeUuids(res);
  };

  const addManySelectedShapeUuids = (uuids: string[]) => {
    const newSelectedShapeUuids = { ...selectedShapeUuids };
    for (const uuid of uuids) {
      newSelectedShapeUuids[uuid] = true;
    }
    setSelectedShapeUuids(newSelectedShapeUuids);
  };

  const removeSelectedShapeUuid = (uuid: string) => {
    const newSelectedShapeUuids = { ...selectedShapeUuids };
    delete newSelectedShapeUuids[uuid];
    setSelectedShapeUuids(newSelectedShapeUuids);
  };

  const clearSelectedShapeUuids = () => {
    setSelectedShapeUuids({});
  };

  const isSelected = (shapeOrUuid: GeoShapeMetadata | string): boolean => {
    if (typeof shapeOrUuid === "string") {
      return selectedShapeUuids[shapeOrUuid];
    }
    return selectedShapeUuids[shapeOrUuid.uuid ?? null];
  };
  const selectedFeatureCollection = geoShapesToFeatureCollection(
    selectedShapeData ? [selectedShapeData] : []
  );

  return (
    <SelectionContext.Provider
      value={{
        selectedShapeUuids,
        setSelectedShapeUuids: (selectedShapes: Record<string, boolean>) =>
          setSelectedShapeUuids(selectedShapes),
        isSelected,
        addSelectedShapeUuid,
        getNumSelectedShapes,
        selectOneShapeUuid,
        addManySelectedShapeUuids,
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
