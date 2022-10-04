import { createContext, useRef, useState } from "react";

interface DeckContextInterface {
  tileCacheKey: number;
  setTileCacheKey: (n: number) => void;
  triggerTileRefresh: () => void;
  deckRef: React.RefObject<any>;
  // deckgl instance
}

export const DeckContext = createContext<DeckContextInterface>({
  tileCacheKey: 0,
  setTileCacheKey: () => {},
  triggerTileRefresh: () => {},
  deckRef: { current: null },
});

DeckContext.displayName = "DeckContext";

export const DeckContextContainer = ({ children }: { children: any }) => {
  const [tileCacheKey, setTileCacheKey] = useState<number>(0);
  const deckRef = useRef<any>();

  function triggerTileRefresh() {
    setTileCacheKey((prevRefreshTiles: any) => prevRefreshTiles + 1);
  }

  return (
    <DeckContext.Provider
      value={{
        tileCacheKey,
        setTileCacheKey: () => {},
        triggerTileRefresh,
        deckRef,
      }}
    >
      {children}
    </DeckContext.Provider>
  );
};
