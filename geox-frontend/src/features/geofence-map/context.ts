import { createContext } from "react";
import { GeoShape } from "../../client";

interface GeofencerContextState {
  selectedShapes: GeoShape[];
  setSelectedShapes: (shapes: GeoShape[]) => void;
  shapeForEdit: GeoShape | null | undefined;
  setShapeForEdit: (shape: GeoShape | null | undefined) => void;
  editableMode: string;
  setEditableMode: (mode: string) => void;
  viewport: any;
  setViewport: (viewport: any) => void;
}

export const GeofencerContext = createContext<GeofencerContextState>({
  selectedShapes: [],
  setSelectedShapes: () => {},
  shapeForEdit: null,
  setShapeForEdit: () => {},
  editableMode: "",
  setEditableMode: () => {},
  viewport: {},
  setViewport: () => {},
});
