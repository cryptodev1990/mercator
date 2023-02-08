import { useGetNamespaces } from "features/geofence-map/hooks/use-openapi-hooks";
import { useEffect } from "react";
import { useShapes } from "../../../../hooks/use-shapes";
import { NamespaceCard } from "./card";
import { ShapeSearchBar } from "./shape-search-bar";
import ReactLoading from "react-loading";

export const NamespaceSection = ({ className }: { className: string }) => {
  const { visibleNamespaceIDs, activeNamespaceIDs, setActiveNamespaceIDs } =
    useShapes();

  const { data: namespaces } = useGetNamespaces();

  if (!namespaces)
    return (
      <div className="flex justify-center">
        <ReactLoading type="bubbles" />
      </div>
    );

  return (
    <div className={className}>
      {namespaces.flatMap((x) => x.shapes ?? []).length > 0 && (
        <ShapeSearchBar />
      )}
      {namespaces.map((namespace, i) => {
        const isVisible = visibleNamespaceIDs.includes(namespace?.id);
        const isActive = activeNamespaceIDs.includes(namespace.id);
        return (
          <NamespaceCard
            key={i}
            namespace={namespace}
            shouldOpen={isActive}
            isVisible={isVisible}
            onClickCaret={() => {
              if (isActive) {
                // remove from active namespaces
                setActiveNamespaceIDs(
                  activeNamespaceIDs.filter(
                    (namespaceID: string) => namespaceID !== namespace.id
                  )
                );
              } else {
                setActiveNamespaceIDs([...activeNamespaceIDs, namespace.id]);
              }
            }}
          />
        );
      })}
    </div>
  );
};
