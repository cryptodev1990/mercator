import { createContext, useRef, useState } from "react";

interface DeckContextInterface {
  deckRef: React.RefObject<any>;
  // deckgl instance
  hoveredUuid: string | null;
  setHoveredUuid: (uuid: string | null) => void;
}

export const DeckContext = createContext<DeckContextInterface>({
  deckRef: { current: null },
  hoveredUuid: null,
  setHoveredUuid: () => {},
});

DeckContext.displayName = "DeckContext";

export const DeckContextProvider = ({ children }: { children: any }) => {
  const deckRef = useRef<any>();
  const [hoveredUuid, setHoveredUuid] = useState<string | null>(null);

  return (
    <DeckContext.Provider
      value={{
        deckRef,
        hoveredUuid,
        setHoveredUuid,
      }}
    >
      {children}
    </DeckContext.Provider>
  );
};
