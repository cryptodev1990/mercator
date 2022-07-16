import { useContext, useMemo } from "react";
import { GeoShape } from "../../../client";
import { GeofencerContext } from "../geofencer-view";

export const useEditModal = () => {
  const { shapeForEdit, setShapeForEdit } = useContext(GeofencerContext);
  return { shapeForEdit, setShapeForEdit };
};

export const useSelectedShapes = () => {
  /**
   *  Handle selection of shapes
   *
   *  Highlighting in the map and sidebar get connected here.
   */
  const { selectedShapes, setSelectedShapes } = useContext(GeofencerContext);

  const selectedShapesSet = useMemo(() => {
    return new Set(selectedShapes.map((shape) => shape.uuid));
  }, [selectedShapes]);

  function isSelected(uuid: string) {
    return selectedShapesSet.has(uuid);
  }

  function selectOne(shape: GeoShape) {
    setSelectedShapes([shape]);
  }

  function appendSelected(shapes: GeoShape[], clobber: boolean = false) {
    if (clobber) {
      setSelectedShapes([...shapes]);
    } else {
      setSelectedShapes([...selectedShapes, ...shapes]);
    }
  }

  function removeAllSelections() {
    setSelectedShapes([]);
  }

  function removeSelection(shape: GeoShape) {
    const newShapes = [];
    for (const oldShape of selectedShapes) {
      if (oldShape.uuid !== shape.uuid) {
        newShapes.push(oldShape);
      }
    }
    setSelectedShapes(newShapes);
  }

  return {
    isSelected,
    selectOne,
    appendSelected,
    removeAllSelections,
    removeSelection,
  };
};
