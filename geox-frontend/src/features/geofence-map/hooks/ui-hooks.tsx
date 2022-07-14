import { useContext, useEffect, useMemo, useState } from "react";
import { DrawPolygonMode, ViewMode } from "@nebula.gl/edit-modes";
import { GeoShape } from "../../../client";
import { GeofencerContext } from "../geofencer-view";

export const useEditModal = () => {
  const { shapeForEdit, setShapeForEdit } = useContext(GeofencerContext);
  return { shapeForEdit, setShapeForEdit };
};

export const useEditMode = () => {
  // TODO need to update nebula.gl to get this to work
  const [editMode, setEditMode] = useState<any>(() => DrawPolygonMode);

  function escFunction(event: KeyboardEvent) {
    if (event.key === "Escape") {
      setEditMode(() => () => ViewMode);
    }
  }

  useEffect(() => {
    document.addEventListener("keydown", escFunction, false);

    return () => {
      document.removeEventListener("keydown", escFunction, false);
    };
  }, []);

  return { editMode, setEditMode };
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

  function appendSelected(shapes: GeoShape[]) {
    setSelectedShapes([...selectedShapes, ...shapes]);
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
