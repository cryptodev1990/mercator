import { useContext } from "react";
import { SelectionContext } from "../contexts/selection/selection.context";

export const useSelectedShapes = () => {
  const ctx = useContext(SelectionContext);
  return {
    ...ctx,
  };
};
