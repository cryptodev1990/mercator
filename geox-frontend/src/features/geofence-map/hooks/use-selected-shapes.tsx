import { useContext } from "react";
import {
  SelectionContext,
  SelectionContextI,
} from "../contexts/selection/selection.context";

export const useSelectedShapes = () => {
  const ctx = useContext<SelectionContextI>(SelectionContext);
  return {
    ...ctx,
  };
};
