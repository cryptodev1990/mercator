import { useContext, useEffect } from "react";
import { GeoShape, GetAllShapesRequestType } from "../../../client";
import { GeofencerContext } from "../context";
import { useGetAllShapesQuery } from "./openapi-hooks";

const useSelectedShapeUuids = () => {
  const { selectedShapeUuids, setSelectedShapeUuids } =
    useContext(GeofencerContext);

  const addSelectedShapeUuid = (uuid: string) => {
    const output = { ...selectedShapeUuids };
    output[uuid] = true;
    setSelectedShapeUuids(output);
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

  const shapeIsSelected = (shape: GeoShape) => {
    if (shape.uuid === undefined) {
      return false;
    }
    return selectedShapeUuids[shape.uuid];
  };

  return {
    shapeIsSelected,
    addSelectedShapeUuid,
    selectOneShapeUuid,
    addManySelectedShapeUuids,
    removeSelectedShapeUuid,
    clearSelectedShapeUuids,
  };
};

export const useShapes = () => {
  // TODO this needs to be global state
  const { data: remoteShapes, isLoading } = useGetAllShapesQuery(
    GetAllShapesRequestType.ORGANIZATION
  );

  useEffect(() => {
    if (remoteShapes === undefined) {
      return;
    }
    for (const shape of remoteShapes) {
      shape.geojson.properties.__uuid = shape.uuid;
    }
    setShapes(remoteShapes);
  }, [remoteShapes]);

  function scrollToSelectedShape(i: number) {
    if (virtuosoRef.current === null) {
      return;
    }
    virtuosoRef.current.scrollToIndex({
      index: i,
      align: "start",
      behavior: "smooth",
    });
  }

  function clearSelectedFeatureIndexes() {
    setSelectedFeatureIndexes([]);
  }

  const {
    shapes,
    tentativeShapes,
    setTentativeShapes,
    guideShapes,
    setGuideShapes,
    selectedShapeUuids,
    setSelectedShapeUuids,
    shapeForMetadataEdit,
    setShapeForMetadataEdit,
    setShapes,
    mapRef,
    virtuosoRef,
    selectedFeatureIndexes,
    setSelectedFeatureIndexes,
  } = useContext(GeofencerContext);

  const {
    addManySelectedShapeUuids,
    addSelectedShapeUuid,
    selectOneShapeUuid,
    removeSelectedShapeUuid,
    clearSelectedShapeUuids,
    shapeIsSelected,
  } = useSelectedShapeUuids();

  const getNumSelectedShapes = () => {
    return Object.keys(selectedShapeUuids).length;
  };

  return {
    shapes,
    isLoading,
    // selection
    getNumSelectedShapes,
    selectedShapeUuids,
    setSelectedShapeUuids,
    addSelectedShapeUuid,
    selectOneShapeUuid,
    addManySelectedShapeUuids,
    removeSelectedShapeUuid,
    clearSelectedShapeUuids,
    shapeIsSelected,
    // metadata editing
    shapeForMetadataEdit,
    setShapeForMetadataEdit,
    tentativeShapes,
    setTentativeShapes,
    virtuosoRef,
    mapRef,
    scrollToSelectedShape,
    guideShapes,
    setGuideShapes,
    selectedFeatureIndexes,
    setSelectedFeatureIndexes,
    clearSelectedFeatureIndexes,
  };
};
