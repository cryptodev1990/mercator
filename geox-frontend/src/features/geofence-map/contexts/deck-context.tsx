import { createContext, useRef } from "react";

interface DeckContextInterface {
  deckRef: React.RefObject<any>;
  // deckgl instance
}

export const DeckContext = createContext<DeckContextInterface>({
  deckRef: { current: null },
});

DeckContext.displayName = "DeckContext";

export const DeckContextProvider = ({ children }: { children: any }) => {
  const deckRef = useRef<any>();

  return (
    <DeckContext.Provider
      value={{
        deckRef,
      }}
    >
      {children}
    </DeckContext.Provider>
  );
};
