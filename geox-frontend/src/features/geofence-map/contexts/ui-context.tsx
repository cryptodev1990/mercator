import { createContext, useEffect, useState } from "react";
import { UIModalEnum } from "../types";

interface UIContextState {
  modal: UIModalEnum | null;
  setModal: (modal: UIModalEnum | null) => void;
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
