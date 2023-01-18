import { useEffect, useCallback, useState, RefObject } from "react";

const useContextMenu = (outerRef: RefObject<HTMLDivElement>) => {
  const [xPos, setXPos] = useState<number>(0);
  const [yPos, setYPos] = useState<number>(0);
  const [menu, showMenu] = useState<Boolean>(false);

  const handleContextMenu = useCallback(
    (event: MouseEvent) => {
      event.preventDefault();
      if (
        outerRef &&
        outerRef.current &&
        outerRef.current.contains(event.target as Node)
      ) {
        setXPos(event.pageX);
        setYPos(event.pageY);
        showMenu(true);
      } else {
        showMenu(false);
      }
    },
    [showMenu, outerRef, setXPos, setYPos]
  );

  const handleClick = useCallback(() => {
    showMenu(false);
  }, [showMenu]);

  useEffect(() => {
    document.addEventListener("click", handleContextMenu);
    document.addEventListener("contextmenu", handleContextMenu);
    return () => {
      document.removeEventListener("click", handleContextMenu);
      document.removeEventListener("contextmenu", handleContextMenu);
    };
  }, []);

  return { xPos, yPos, menu };
};

export default useContextMenu;
