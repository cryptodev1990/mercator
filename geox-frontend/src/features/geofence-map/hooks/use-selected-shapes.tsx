import { useContext } from "react";
import { SelectionContext } from "../contexts/selection-context";

export const useSelectedShapes = () => {
  const ctx = useContext(SelectionContext);
  const selectedUuids = Object.keys(ctx.selectedShapeUuids);
  return {
    ...ctx,
    selectedUuids,
  };
};
