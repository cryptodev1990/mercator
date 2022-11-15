import React, { RefObject } from "react";
import useContextMenu from "../../hooks/use-context-menu";
import { useShapes } from "../../hooks/use-shapes";

const Menu = ({ outerRef }: { outerRef: RefObject<HTMLDivElement> }) => {
  const { namespaces } = useShapes();
  const { xPos, yPos, menu } = useContextMenu(outerRef);

  if (menu) {
    return (
      <div className="z-10 w-44 bg-white rounded divide-y divide-gray-100 shadow dark:bg-gray-700">
        <ul
          className="py-1 text-sm text-gray-700 dark:text-gray-200"
          style={{ top: yPos, left: xPos }}
        >
          {namespaces.map((namespace, i) => (
            <li
              className="block py-2 px-4 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white whitespace-nowrap"
              key={namespace.id}
              onClick={() => console.log(`${namespace.name} clicked`)}
            >
              {namespace.name}
            </li>
          ))}
        </ul>
      </div>
    );
  }
  return <></>;
};

export default Menu;
