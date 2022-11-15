import React, { RefObject } from "react";
import useContextMenu from "../../hooks/use-context-menu";

const Menu = ({ outerRef }: { outerRef: RefObject<HTMLDivElement> }) => {
  const { xPos, yPos, menu } = useContextMenu(outerRef);

  if (menu) {
    return (
      <ul
        className="menu bg-black text-white w-fit"
        style={{ top: yPos, left: xPos }}
      >
        <li>Item1</li>
        <li>Item2</li>
        <li>Item3</li>
      </ul>
    );
  }
  return <></>;
};

export default Menu;
