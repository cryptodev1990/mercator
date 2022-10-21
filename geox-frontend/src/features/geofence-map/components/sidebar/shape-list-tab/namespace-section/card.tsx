import { useState } from "react";
import { BsEyeFill, BsEyeSlashFill } from "react-icons/bs";
import { TbCaretRight } from "react-icons/tb";
import { Virtuoso } from "react-virtuoso";
import { Namespace } from "../../../../../../client";
import { EditableLabel } from "../../../../../../common/components/editable-label";
import { useSelectedShapes } from "../../../../hooks/use-selected-shapes";
import { useShapes } from "../../../../hooks/use-shapes";
import { DragTarget } from "../shape-card/drag-handle";
import { ShapeCard } from "../shape-card/shape-card";
import { DeleteButton } from "./delete-button";
import simplur from "simplur";

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

  const sectionShapeMetadata = shapeMetadata.filter(
    (shape) => shape.namespace_id === namespace.id
  );

  return (
    <DragTarget
      id={`namespace-card-${namespace.slug}`}
      className={`snap-start bg-slate-600 border-gray-200`}
      handleDragOver={(e: any) => {
        const data = e.dataTransfer.getData("text");
        partialUpdateShape({ uuid: data, namespace: namespace.id });
      }}
    >
      {/* Namespace header */}
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
          {hovered && (
            <span className="text-sm">{simplur`${sectionShapeMetadata.length} shape[|s]`}</span>
          )}
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
            <span data-tip="Click to show/hide layer" data-tip-skew="right">
              {isVisible ? <BsEyeFill /> : <BsEyeSlashFill />}
            </span>
          </div>
        </div>
      </div>
      <hr />
      {/* Directory body */}
      {shouldOpen && (
        <Virtuoso
          style={{
            height: 3 * sectionShapeMetadata.length + "rem",
          }}
          data={sectionShapeMetadata}
          itemContent={(index, data) => {
            const shape = data;
            return (
              <ShapeCard
                shape={shape}
                key={index}
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
      )}
    </DragTarget>
  );
};
