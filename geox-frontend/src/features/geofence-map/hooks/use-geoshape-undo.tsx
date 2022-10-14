import { useContext } from "react";
import { UndoContext } from "../contexts/geoshape/undo.context";

export const useGeoShapeUndo = () => {
  const ctx = useContext(UndoContext);
  return ctx;
};
