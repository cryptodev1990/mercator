import { createContext } from "react";
import { GeoShape, GeoShapeCreate, GeoShapeUpdate } from "../../client";

export interface MapEditOptions {
  /**
   * denyOverlap - Block shapes from overlapping with each other
   */
  denyOverlap?: boolean;
}

interface GeofencerContextState {
  selectedShapes: GeoShape[];
  setSelectedShapes: (shapes: GeoShape[]) => void;
  tentativeShapes: GeoShapeCreate[];
  setTentativeShapes: (shapes: GeoShapeCreate[]) => void;
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
  tentativeShapes: [],
  setTentativeShapes: () => {},
  shapeForEdit: null,
  setShapeForEdit: () => {},
  editableMode: "",
  setEditableMode: () => {},
  viewport: {},
  setViewport: () => {},
  options: {},
  setOptions: () => {},
});
