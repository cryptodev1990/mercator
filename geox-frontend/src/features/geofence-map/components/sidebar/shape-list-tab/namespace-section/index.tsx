import { useGetNamespaces } from "features/geofence-map/hooks/use-openapi-hooks";
import { useShapes } from "../../../../hooks/use-shapes";
import { NamespaceCard } from "./card";
import { ShapeSearchBar } from "./shape-search-bar";

export const NamespaceSection = ({ className }: { className: string }) => {
  const { visibleNamespaces, activeNamespaces, setActiveNamespaces } =
    useShapes();

  const { data: namespaces } = useGetNamespaces();

  if (!namespaces) return null;

  return (
    <div className={className}>
      {namespaces.flatMap((x) => x.shapes ?? []).length > 0 && (
        <ShapeSearchBar />
      )}
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
    </div>
  );
};
