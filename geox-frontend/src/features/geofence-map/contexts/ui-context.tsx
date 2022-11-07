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
  isochroneParams: {
    timeInMinutes: 5,
    travelMode: "car",
  },
  setIsochroneParams: () => {},
});
UIContext.displayName = "UIContext";

export const UIContextContainer = ({ children }: { children: any }) => {
  const [modal, setModal] = useState<UIModalEnum | null>(null);
  const [isochroneParams, setIsochroneParams] = useState({
    timeInMinutes: 5,
    travelMode: "car",
  });

  // Check local storage for an indicator on the docs
  const [showDocs, setShowDocs] = useState(false);

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
        setShowDocs: (showDocs: boolean) => setShowDocs(showDocs),
        isochroneParams,
        setIsochroneParams: (params: {
          timeInMinutes: number;
          travelMode: string;
        }) => setIsochroneParams(params),
      }}
    >
      {children}
    </UIContext.Provider>
  );
};
