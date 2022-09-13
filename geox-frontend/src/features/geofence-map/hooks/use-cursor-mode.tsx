import { useContext } from "react";
import { GeofencerContext } from "../context";
import { EditorMode } from "../cursor-modes";

export const useCursorMode = () => {
  const { options, setOptions } = useContext(GeofencerContext);
  const cursorMode = options.cursorMode;
  const setCursorMode = (mode: EditorMode) => {
    setOptions({ ...options, cursorMode: mode });
  };

  return { cursorMode, setCursorMode, options, setOptions };
};
