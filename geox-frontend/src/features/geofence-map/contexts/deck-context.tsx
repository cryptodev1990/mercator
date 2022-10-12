import { createContext, useEffect, useRef } from "react";

interface DeckContextInterface {
  deckRef: React.RefObject<any>;
  // deckgl instance
}

export const DeckContext = createContext<DeckContextInterface>({
  deckRef: { current: null },
});

DeckContext.displayName = "DeckContext";

export const DeckContextContainer = ({ children }: { children: any }) => {
  const deckRef = useRef<any>();

  useEffect(() => {
    console.log("deckRef", deckRef);
  }, [deckRef]);

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
