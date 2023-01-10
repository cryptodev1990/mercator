import { useContext, useEffect } from "react";
import { GeofencerContext } from "../contexts/geofencer-context";
import { EditorMode } from "../cursor-modes";

export const useCursorMode = () => {
  const { options, setOptions } = useContext(GeofencerContext);
  const { cursorMode } = options;
  const setCursorMode = (mode: EditorMode) => {
    setOptions({ ...options, cursorMode: mode });
  };
  return { cursorMode, setCursorMode, options, setOptions };
};
