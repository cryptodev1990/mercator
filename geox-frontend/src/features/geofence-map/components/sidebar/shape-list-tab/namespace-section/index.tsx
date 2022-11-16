import { useShapes } from "../../../../hooks/use-shapes";
import { AddButton } from "./add-button";
import { NamespaceCard } from "./card";
import { ShapeSearchBar } from "./shape-search-bar";

export const NamespaceSection = ({ className }: { className: string }) => {
  const {
    namespaces,
    visibleNamespaces,
    activeNamespaces,
    setActiveNamespaces,
    shapeMetadata,
  } = useShapes();

  return (
    <div className={className}>
      {shapeMetadata.length > 0 && <ShapeSearchBar />}
      {namespaces.map((namespace, i) => {
        const isVisible = visibleNamespaces
          .map((x) => x.id)
          .includes(namespace?.id);
        const isActive = activeNamespaces
          .map((n) => n.id)
          .includes(namespace.id);
        return (
          <NamespaceCard
            key={i}
            namespace={namespace}
            shouldOpen={isActive}
            isVisible={isVisible}
            onClickCaret={() => {
              if (isActive) {
                // remove from active namespaces
                setActiveNamespaces(
                  activeNamespaces.filter((n) => n.id !== namespace.id)
                );
              } else {
                setActiveNamespaces([...activeNamespaces, namespace]);
              }
            }}
          />
        );
      })}
      <AddButton />
    </div>
  );
};
