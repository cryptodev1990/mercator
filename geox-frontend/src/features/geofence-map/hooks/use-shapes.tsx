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
    console.log(newSelectedShapeUuids);
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
    GetAllShapesRequestType.DOMAIN
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

  const {
    shapes,
    tentativeShapes,
    setTentativeShapes,
    selectedShapeUuids,
    setSelectedShapeUuids,
    shapeForMetadataEdit,
    setShapeForMetadataEdit,
    setShapes,
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
  };
};