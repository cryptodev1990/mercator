import { useSelectedShapes } from "./use-selected-shapes";

export function useSelectedShapesUuids() {
  const { selectedShapes } = useSelectedShapes();
  return selectedShapes.map((shape: any) => shape.properties.__uuid);
}
