import { useEffect, useState } from "react";
import { BsEyeFill, BsEyeSlashFill } from "react-icons/bs";
import { TbCaretRight } from "react-icons/tb";
import { Virtuoso } from "react-virtuoso";
import { GeoShape, GeoShapeMetadata, Namespace } from "../../../../../client";
import { useSelectedShapes } from "../../../hooks/use-selected-shapes";
import { useShapes } from "../../../hooks/use-shapes";
import { ShapeCard } from "./shape-card";

export const NamespaceSection = () => {
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
    <div className="flex flex-col">
      {namespaces.map((namespace, i) => {
        const isVisible = visibleNamepaces
          .map((x) => x.id)
          .includes(namespace?.id);
        const isActive = activeNamespace?.id === namespace.id;
        return (
          <NamespaceDirectoryCard
            namespace={namespace}
            shouldOpen={isActive}
            isVisible={isVisible}
            onClickCaret={() => setActiveNamespace(isActive ? null : namespace)}
          />
        );
      })}
    </div>
  );
};

const NamespaceDirectoryCard = ({
  namespace,
  onClickCaret,
  isVisible,
  shouldOpen,
}: {
  namespace: Namespace;
  onClickCaret: () => void;
  shouldOpen: boolean;
  isVisible: boolean;
}) => {
  const { shapeMetadata, visibleNamepaces, setVisibleNamespaces } = useShapes();
  const [shapeHovered, setShapeHovered] = useState<string | null>(null);

  const { selectOneShapeUuid } = useSelectedShapes();

  return (
    <>
      <div className="flex cursor-pointer px-3">
        <button
          onClick={onClickCaret}
          className={`transition ${shouldOpen ? "rotate-90" : ""}`}
        >
          <TbCaretRight />
        </button>
        <div>
          <p className="font-bold text-md mx-1 select-none">{namespace.name}</p>
        </div>
        <div
          onClick={() => {
            if (isVisible) {
              setVisibleNamespaces(
                visibleNamepaces.filter((x) => x.id !== namespace.id)
              );
            } else {
              setVisibleNamespaces([...visibleNamepaces, namespace]);
            }
          }}
          className="self-center ml-auto z-10"
        >
          {isVisible ? <BsEyeFill /> : <BsEyeSlashFill />}
        </div>
      </div>
      <hr />
      {shouldOpen && (
        <div
          key={1}
          className="relative short-h:60vh md-h:65vh tall-h:h-[70vh]"
        >
          <Virtuoso
            className="h-full scrollbar-thin scrollbar-thumb-slate-400 scrollbar-track-slate-700"
            totalCount={shapeMetadata.length}
            data={shapeMetadata.filter(
              (shape) => shape.namespace_id === namespace.id
            )}
            itemContent={(_: any, shape: GeoShapeMetadata) => {
              return (
                <ShapeCard
                  shape={shape}
                  key={shape.uuid}
                  isHovered={shapeHovered === shape.uuid}
                  onMouseEnter={() => {
                    setShapeHovered(shape.uuid);
                    selectOneShapeUuid(shape.uuid);
                  }}
                  onMouseLeave={() => setShapeHovered(null)}
                />
              );
            }}
          />
        </div>
      )}
    </>
  );
};
