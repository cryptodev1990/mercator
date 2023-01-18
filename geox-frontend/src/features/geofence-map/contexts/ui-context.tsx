import { createContext, useEffect, useState } from "react";
import { UIModalEnum } from "../types";

interface UIContextState {
  modal: UIModalEnum | null;
  setModal: (modal: UIModalEnum | null) => void;
  showDocs: boolean;
  setShowDocs: (showDocs: boolean) => void;
  isochroneParams: {
    timeInMinutes: number;
    travelMode: string;
  };
  heading: string;
  setHeading: (heading: string) => void;
  // delete prompt
  deletePromptCoords: number[];
  confirmDelete: (coords: number[], onConfirm: () => void) => void;
  onDeleteConfirm: () => void;
  onDeleteCancel: () => void;
  setIsochroneParams: (params: {
    timeInMinutes: number;
    travelMode: string;
  }) => void;
}

export const UIContext = createContext<UIContextState>({
  modal: null,
  setModal: () => {},
  showDocs: false,
  setShowDocs: () => {},
  confirmDelete: () => {},
  deletePromptCoords: [],
  onDeleteConfirm: () => {},
  onDeleteCancel: () => {},
  isochroneParams: {
    timeInMinutes: 5,
    travelMode: "car",
  },
  heading: "",
  setHeading: () => {},
  setIsochroneParams: () => {},
});
UIContext.displayName = "UIContext";

export const UIContextContainer = ({ children }: { children: any }) => {
  const [heading, setHeading] = useState("");
  const [modal, setModal] = useState<UIModalEnum | null>(null);
  const [isochroneParams, setIsochroneParams] = useState({
    timeInMinutes: 5,
    travelMode: "car",
  });

  // Check local storage for an indicator on the docs
  const [showDocs, setShowDocs] = useState(false);

  const [deletePromptCoords, setDeletePromptCoords] = useState<number[]>([]);
  const [onDeleteConfirm, setOnDeleteConfirm] = useState<() => void>(
    () => () => {}
  );

  function confirmDelete(coords: number[], onConfirm: () => void) {
    setDeletePromptCoords(coords);
    setOnDeleteConfirm(() => () => {
      onConfirm();
      setOnDeleteConfirm(() => () => {});
      setDeletePromptCoords([]);
    });
  }

  function onDeleteCancel() {
    setOnDeleteConfirm(() => () => {});
    setDeletePromptCoords([]);
  }

  useEffect(() => {
    const showDocsLocal = localStorage.getItem("showDocs");
    if (!showDocsLocal) {
      setShowDocs(true);
      localStorage.setItem("showDocs", "true");
    }
    if (showDocs) {
      setShowDocs(showDocsLocal === "true");
    }
  }, []);

  useEffect(() => {
    localStorage.setItem("showDocs", showDocs.toString());
  }, [showDocs]);

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") {
        setModal(null);
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  return (
    <UIContext.Provider
      value={{
        modal,
        setModal: (modalEnumValue: UIModalEnum | null) =>
          setModal(modalEnumValue),
        showDocs,
        setShowDocs,
        // delete prompt
        confirmDelete: (deletePromptCoords: number[], onConfirm: () => void) =>
          confirmDelete(deletePromptCoords, onConfirm),
        deletePromptCoords,
        onDeleteConfirm,
        onDeleteCancel,
        // isochrone
        isochroneParams,
        setIsochroneParams: (params: {
          timeInMinutes: number;
          travelMode: string;
        }) => setIsochroneParams(params),
        heading,
        setHeading,
      }}
    >
      {children}
    </UIContext.Provider>
  );
};
