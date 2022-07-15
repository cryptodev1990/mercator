import { useContext, useEffect } from "react";
import { GeofencerContext } from "../geofencer-view";
import { MODES } from "./modes";

export const useEditableMode = () => {
  // TODO need to update nebula.gl to get this to work
  const { editableMode, setEditableMode } = useContext(GeofencerContext);

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

  return { editableMode, setEditableMode };
};
