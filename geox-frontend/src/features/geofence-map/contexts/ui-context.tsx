import { createContext, useEffect, useState } from "react";
import { UIModalEnum } from "../types";

interface UIContextState {
  modal: UIModalEnum | null;
  setModal: (modal: UIModalEnum | null) => void;
}

export const UIContext = createContext<UIContextState>({
  modal: null,
  setModal: () => {},
});
UIContext.displayName = "UIContext";

export const UIContextContainer = ({ children }: { children: any }) => {
  const [modal, setModal] = useState<UIModalEnum | null>(null);

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

  useEffect(() => {
    console.log("modal", modal);
  }, [modal]);

  return (
    <UIContext.Provider
      value={{
        modal,
        setModal: (modalEnumValue: UIModalEnum | null) =>
          setModal(modalEnumValue),
      }}
    >
      {children}
    </UIContext.Provider>
  );
};
