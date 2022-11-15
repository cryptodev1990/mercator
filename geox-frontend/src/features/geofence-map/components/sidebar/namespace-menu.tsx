import React, { RefObject, useContext } from "react";
import useContextMenu from "../../hooks/use-context-menu";
import { useShapes } from "../../hooks/use-shapes";
import { NamespaceContext } from "./shape-list-tab/namespace-section/namespace-context";

const NamespaceMenu = ({
  outerRef,
}: {
  outerRef: RefObject<HTMLDivElement>;
}) => {
  const currentNamespace = useContext(NamespaceContext);
  const { namespaces } = useShapes();
  const { xPos, yPos, menu } = useContextMenu(outerRef);

  if (menu) {
    return (
      <div className="z-1000 w-44 bg-white rounded divide-y divide-gray-100 shadow dark:bg-gray-700">
        <ul
          className="py-1 text-sm text-gray-700 dark:text-gray-200"
          style={{ top: yPos, left: xPos }}
        >
          {namespaces
            .filter(
              (namespace) =>
                currentNamespace && namespace.id != currentNamespace.id
            )
            .map((namespace, i) => (
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

export default NamespaceMenu;
