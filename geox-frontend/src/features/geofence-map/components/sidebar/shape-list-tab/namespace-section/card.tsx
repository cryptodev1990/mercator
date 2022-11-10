import { useContext, useEffect, useRef, useState } from "react";
import {
  EyeFillIcon,
  EyeSlashFillIcon,
  CaretRightIcon,
} from "../../../../../../common/components/icons";
import { Namespace } from "../../../../../../client";
import { EditableLabel } from "../../../../../../common/components/editable-label";
import { useShapes } from "../../../../hooks/use-shapes";
import { DragTarget } from "../shape-card/drag-handle";
import { ShapeCard } from "../shape-card/shape-card";
import { DeleteButton } from "./delete-button";
import simplur from "simplur";
import { useSelectedShapes } from "../../../../hooks/use-selected-shapes";
import { SearchContext } from "../../../../contexts/search-context";
import { MdFastForward, MdFastRewind } from "react-icons/md";

const MAX_DISPLAY_SHAPES = 20;

const PageSelector = ({
  page,
  setPage,
  maxPage,
  maxShapes,
}: {
  page: number;
  setPage: (page: number) => void;
  maxPage: number;
  maxShapes: number;
}) => {
  const coreCss =
    "flex items-center justify-center w-8 h-8 rounded-full bg-gray-600 hover:bg-gray-500 ";
  const leftBtnCls =
    coreCss + (page === 0 ? "text-gray-500 hover:bg-transparent" : "");
  const rightBtnCls =
    coreCss + (page === maxPage ? "text-gray-500 hover:bg-transparent" : "");

  return (
    <div className="flex items-center justify-center w-full">
      <button className={leftBtnCls} onClick={() => setPage(0)}>
        <MdFastRewind />
      </button>
      <button
        className={leftBtnCls}
        onClick={() => setPage(Math.max(0, page - 1))}
      >
        <CaretRightIcon className="w-4 h-4 transform rotate-180" />
      </button>
      <div className="mx-2 select-none">
        {page * MAX_DISPLAY_SHAPES + 1} -{" "}
        {Math.min(MAX_DISPLAY_SHAPES + page * MAX_DISPLAY_SHAPES, maxShapes)}
      </div>
      <button
        className={rightBtnCls}
        onClick={() => setPage(Math.min(maxPage, page + 1))}
      >
        <CaretRightIcon className="w-4 h-4" />
      </button>
      <button className={rightBtnCls} onClick={() => setPage(maxPage)}>
        <MdFastForward />
      </button>
    </div>
  );
};

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
  const { selectOneShapeUuid } = useSelectedShapes();
  const [shapeHovered, setShapeHovered] = useState<string | null>(null);
  const [hovered, setHovered] = useState(false);
  const { searchResults } = useContext(SearchContext);
  // support pages
  const [page, setPage] = useState(0);
  const [maxPage, setMaxPage] = useState(0);

  useEffect(() => {
    const sectionShapeMetadata = shapeMetadata.filter(
      (shape) => shape.namespace_id === namespace.id
    );

    if (shouldOpen) {
      setMaxPage(Math.ceil(sectionShapeMetadata.length / MAX_DISPLAY_SHAPES));
    }
  }, [namespace.shapes]);

  useEffect(() => {
    // select a shape if hovered
    if (shapeHovered) {
      selectOneShapeUuid(shapeHovered);
    }
  }, [shapeHovered]);

  const sectionShapeMetadata = shapeMetadata.filter(
    (shape) => shape.namespace_id === namespace.id
  );

  return (
    <DragTarget
      id={`namespace-card-${namespace.slug}`}
      className={`snap-start bg-slate-600 border-gray-200`}
      handleDragOver={(e: React.DragEvent) => {
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
          <CaretRightIcon />
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
              {isVisible ? <EyeFillIcon /> : <EyeSlashFillIcon />}
            </span>
          </div>
        </div>
      </div>
      <hr />
      {/* Directory body */}
      {shouldOpen && (
        <div>
          {sectionShapeMetadata.length > 0 &&
            sectionShapeMetadata
              .filter((x, i) => {
                if (searchResults) {
                  return searchResults.has(x.uuid);
                } else {
                  return (
                    i >= page * MAX_DISPLAY_SHAPES &&
                    i < (page + 1) * MAX_DISPLAY_SHAPES
                  );
                }
              })
              .map((x) => (
                <ShapeCard
                  shape={x}
                  onMouseEnter={() => setShapeHovered(x.uuid)}
                  onMouseLeave={() => setShapeHovered(null)}
                  isHovered={shapeHovered === x.uuid}
                  key={x.uuid}
                />
              ))}
          {!searchResults &&
            sectionShapeMetadata.length > MAX_DISPLAY_SHAPES && (
              <PageSelector
                maxShapes={sectionShapeMetadata.length}
                page={page}
                setPage={setPage}
                maxPage={maxPage}
              />
            )}
        </div>
      )}
    </DragTarget>
  );
};
