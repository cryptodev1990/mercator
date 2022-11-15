import { useEffect, useCallback, useState, RefObject } from "react";

const useContextMenu = (outerRef: RefObject<HTMLDivElement>) => {
  const [xPos, setXPos] = useState<string>("0px");
  const [yPos, setYPos] = useState<string>("0px");
  const [menu, showMenu] = useState<Boolean>(false);

  const handleContextMenu = useCallback(
    (event: MouseEvent) => {
      event.preventDefault();
      if (
        outerRef &&
        outerRef.current &&
        outerRef.current.contains(event.target as Node)
      ) {
        setXPos(`${event.pageX}px`);
        setYPos(`${event.pageY}px`);
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
    document.addEventListener("click", handleClick);
    document.addEventListener("contextmenu", handleContextMenu);
    return () => {
      document.removeEventListener("click", handleClick);
      document.removeEventListener("contextmenu", handleContextMenu);
    };
  }, []);

  return { xPos, yPos, menu };
};

export default useContextMenu;
