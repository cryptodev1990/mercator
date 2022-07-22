import { createContext } from "react";
import { GeoShape, GeoShapeUpdate } from "../../client";

export interface MapEditOptions {
  /**
   * denyOverlap - Block shapes from overlapping with each other
   */
  denyOverlap?: boolean;
}

interface GeofencerContextState {
  selectedShapes: GeoShape[];
  setSelectedShapes: (shapes: GeoShape[]) => void;
  shapeForEdit: GeoShapeUpdate | null | undefined;
  setShapeForEdit: (shape: GeoShapeUpdate | null | undefined) => void;
  editableMode: string;
  setEditableMode: (mode: string) => void;
  viewport: any;
  setViewport: (viewport: any) => void;
  options: MapEditOptions;
  setOptions: (options: MapEditOptions) => void;
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
  options: {},
  setOptions: () => {},
});
