import { useContext, useEffect } from "react";
import { GeofencerContext } from "../context";
import { MODES } from "./modes";

export const useEditableMode = () => {
  const { editableMode, setEditableMode, options } =
    useContext(GeofencerContext);

  function escFunction(event: KeyboardEvent) {
    if (event.key === "Escape") {
      setEditableMode(MODES.ViewMode);
    }
  }

  useEffect(() => {
    document.addEventListener("keydown", escFunction, false);

    return () => {
      document.removeEventListener("keydown", escFunction, false);
    };
  }, []);

  return { editableMode, setEditableMode, options };
};
