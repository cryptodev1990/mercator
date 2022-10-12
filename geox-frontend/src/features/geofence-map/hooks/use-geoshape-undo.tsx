import { useContext } from "react";
import { UndoContext } from "../contexts/geoshape/undo.context";

export const useGeoShapeUndo = () => {
  const { undo, redo, startSnapshot, endSnapshot } = useContext(UndoContext);
  return { undo, redo, startSnapshot, endSnapshot };
};
