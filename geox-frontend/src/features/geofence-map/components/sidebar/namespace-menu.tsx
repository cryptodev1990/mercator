import { RefObject } from "react";
import { GeoShapeMetadata } from "../../../../client";
import useContextMenu from "../../hooks/use-context-menu";
import { useShapes } from "../../hooks/use-shapes";

const NamespaceMenu = ({
  outerRef,
  shape,
}: {
  outerRef: RefObject<HTMLDivElement>;
  shape: GeoShapeMetadata;
}) => {
  const { namespaces, partialUpdateShape } = useShapes();
  const { xPos, yPos, menu } = useContextMenu(outerRef);

  if (menu) {
    return (
      <div
        className="absolute w-44 bg-white rounded divide-y divide-gray-100 shadow dark:bg-gray-700 z-50"
        style={{ top: yPos - 15, left: xPos - 15 }}
      >
        <div className="py-1 text-gray-700 dark:text-gray-200 text-center font-medium">
          Move Shape
        </div>
        <ul className="py-1 text-sm text-gray-700 dark:text-gray-200">
          {namespaces
            .filter(
              (namespace) =>
                shape.namespace_id && shape.namespace_id !== namespace.id
            )
            .map((namespace, i) => (
              <li
                className="block py-2 px-4 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white whitespace-nowrap cursor-pointer"
                key={namespace.id}
                onClick={() =>
                  partialUpdateShape({
                    uuid: shape.uuid,
                    namespace: namespace.id,
                  })
                }
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
