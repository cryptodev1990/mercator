import { useState } from "react";
import { BsEyeFill, BsEyeSlashFill } from "react-icons/bs";
import { TbCaretRight } from "react-icons/tb";
import { Virtuoso } from "react-virtuoso";
import {
  GeofencerService,
  GeoShapeMetadata,
  Namespace,
  NamespacesService,
} from "../../../../../../client";
import { EditableLabel } from "../../../../../../common/components/editable-label";
import { useSelectedShapes } from "../../../../hooks/use-selected-shapes";
import { useShapes } from "../../../../hooks/use-shapes";
import { DragTarget } from "../drag-handle";
import { ShapeCard } from "../shape-card";
import { DeleteButton } from "./delete-button";

export const NamespaceCard = ({
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
  const {
    shapeMetadata,
    visibleNamepaces,
    setVisibleNamespaces,
    updateNamespace,
    partialUpdateShape,
  } = useShapes();
  const [shapeHovered, setShapeHovered] = useState<string | null>(null);

  const { selectOneShapeUuid } = useSelectedShapes();
  const [hovered, setHovered] = useState(false);

  return (
    <DragTarget
      handleDragOver={(e: any) => {
        const data = e.dataTransfer.getData("text");
        partialUpdateShape({ uuid: data, namespace: namespace.id });
      }}
    >
      <div
        className="flex cursor-pointer px-3"
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
      >
        <button
          onClick={onClickCaret}
          className={`transition ${shouldOpen ? "rotate-90" : ""}`}
        >
          <TbCaretRight />
        </button>
        <div>
          <EditableLabel
            className="font-bold text-md mx-1 select-none text-white"
            value={namespace.name}
            onChange={(newName) => {
              if (newName !== namespace.name) {
                updateNamespace(namespace.id, { name: newName });
              }
            }}
            disabled={namespace.is_default}
          />
        </div>
        <div className="self-center ml-auto z-10 flex space-x-3">
          {!namespace.is_default && hovered && (
            <DeleteButton namespace={namespace} />
          )}
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
          >
            {isVisible ? <BsEyeFill /> : <BsEyeSlashFill />}
          </div>
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
    </DragTarget>
  );
};
