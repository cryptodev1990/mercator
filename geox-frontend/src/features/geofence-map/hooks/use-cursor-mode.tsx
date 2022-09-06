import { useContext, useEffect } from "react";
import { GeofencerContext } from "../context";
import { EditorMode } from "../cursor-modes";

export const useCursorMode = () => {
  const { options, setOptions } = useContext(GeofencerContext);
  const { setGuideShapes } = useContext(GeofencerContext);

  function escFunction(event: KeyboardEvent) {
    if (event.key === "Escape") {
      // TODO how to get this to work with TypeScript?
      // @ts-ignore
      setOptions((prevOptions: any) => {
        return { ...prevOptions, cursorMode: EditorMode.ViewMode };
      });
    }
  }

  useEffect(() => {
    if (options.cursorMode === EditorMode.ViewMode) {
      setGuideShapes([]);
    }
  }, [options.cursorMode]);

  const cursorMode = options.cursorMode;
  const setCursorMode = (mode: EditorMode) => {
    setOptions({ ...options, cursorMode: mode });
  };

  useEffect(() => {
    document.addEventListener("keydown", escFunction, false);

    return () => {
      document.removeEventListener("keydown", escFunction, false);
    };
  }, []);

  return { cursorMode, setCursorMode, options };
};
