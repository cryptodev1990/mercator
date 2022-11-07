import { useEffect } from "react";
import { useShapes } from "../../../../hooks/use-shapes";
import { AddButton } from "./add-button";
import { NamespaceCard } from "./card";

export const NamespaceSection = ({ className }: { className: string }) => {
  const {
    namespaces,
    visibleNamepaces,
    setVisibleNamespaces,
    activeNamespace,
    setActiveNamespace,
  } = useShapes();

  useEffect(() => {
    if (namespaces.length > 0) {
      setActiveNamespace(namespaces[0]);
      setVisibleNamespaces([namespaces[0]]);
    }
  }, []);

  return (
    <div className={className}>
      {namespaces.map((namespace, i) => {
        const isVisible = visibleNamepaces
          .map((x) => x.id)
          .includes(namespace?.id);
        const isActive = activeNamespace?.id === namespace.id;
        return (
          <NamespaceCard
            key={i}
            namespace={namespace}
            shouldOpen={isActive}
            isVisible={isVisible}
            onClickCaret={() => setActiveNamespace(isActive ? null : namespace)}
          />
        );
      })}
      <AddButton />
    </div>
  );
};
