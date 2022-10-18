import { MdDelete, MdDragIndicator } from "react-icons/md";
import Loading from "react-loading";
import { MetadataEditButton } from "./edit-button";
import simplur from "simplur";

import toast from "react-hot-toast";
import { TbTarget } from "react-icons/tb";
import { useViewport } from "../../../hooks/use-viewport";
import { useCursorMode } from "../../../hooks/use-cursor-mode";
import { EditorMode } from "../../../cursor-modes";
import { GeoShapeMetadata } from "../../../../../client/models/GeoShapeMetadata";
import { useSelectedShapes } from "../../../hooks/use-selected-shapes";
import { useShapes } from "../../../hooks/use-shapes";
import { EditableLabel } from "../../../../../common/components/editable-label";
import { DragHandle } from "./drag-handle";
import { SHAPE_CARD_IMAGE } from "./drag-images";

export const ShapeCard = ({
  shape,
  onMouseEnter,
  onMouseLeave,
  isHovered,
}: {
  shape: GeoShapeMetadata;
  onMouseEnter: (e: any) => void;
  onMouseLeave: (e: any) => void;
  isHovered: boolean;
}) => {
  const {
    deleteShapes,
    updateLoading,
    clearSelectedFeatureIndexes,
    updateShape,
  } = useShapes();

  const { selectedFeatureCollection } = useSelectedShapes();

  const { isSelected, selectedDataIsLoading, clearSelectedShapeUuids } =
    useSelectedShapes();
  const { setCursorMode } = useCursorMode();
  const { snapToBounds } = useViewport();

  const selectionBg = isSelected(shape) ? "bg-slate-600" : "bg-slate-800";
  const selectionOpacity = isSelected(shape) ? "opacity-100" : "opacity-50";
  const numProperties = Object.keys(shape.properties).filter(
    (x) => !x.startsWith("__")
  ).length;
  return (
    <div
      draggable={false}
      key={shape.uuid}
      onMouseLeave={onMouseLeave}
      onMouseEnter={onMouseEnter}
      className={`h-13 p-3 max-w-sm snap-start bg-slate-600 border-gray-200 ${selectionBg}`}
    >
      <div className="flex flex-row justify-left items-center">
        <DragHandle transferData={shape.uuid} dragImage={SHAPE_CARD_IMAGE} />
        <EditableLabel
          value={shape?.name || shape?.properties?.name || "New shape"}
          disabled={selectedDataIsLoading}
          onChange={(newName) => {
            const geojson = selectedFeatureCollection?.features.find(
              (x) => x?.properties?.__uuid === shape.uuid
            );

            if (!geojson) {
              return;
            }

            // @ts-ignore
            geojson.properties.name = newName;

            if (newName !== shape.name) {
              updateShape({
                ...shape,
                // @ts-ignore
                geojson,
                name: newName,
              });
            }
          }}
          className="text-1xl font-sans tracking-tight text-white truncate"
        ></EditableLabel>
        <div
          className={`transition flex flex-row justify-start space-x-1 ${selectionOpacity} ml-auto`}
        >
          {isHovered && (
            <>
              <MetadataEditButton shape={shape} />
              <button
                className="btn btn-square btn-sm bg-slate-700 hover:bg-red-400 hover:border-red-400 box-border"
                title="Delete"
                disabled={updateLoading}
                onClick={() => {
                  if (!shape.uuid) toast.error("Delete shape failed");
                  else {
                    deleteShapes([shape.uuid]);
                    clearSelectedShapeUuids();
                    clearSelectedFeatureIndexes();
                    setCursorMode(EditorMode.ViewMode);
                  }
                }}
              >
                {updateLoading ? (
                  <Loading height={8} width={8} />
                ) : (
                  <MdDelete className="fill-white" />
                )}
              </button>
              <button
                className="btn btn-square btn-sm bg-slate-700 hover:bg-green-400 hover:border-green-400 box-border"
                title="Zoom to"
                disabled={selectedDataIsLoading}
                onClick={() => {
                  snapToBounds({ category: "selected" });
                }}
              >
                <TbTarget
                  className={
                    selectedDataIsLoading
                      ? "fill-gray-400 animate-pulse"
                      : "fill-white"
                  }
                />
              </button>
            </>
          )}
          {!isHovered && numProperties > 0 && (
            <div className="text-xs font-sans tracking-tight text-white box-border">
              {simplur`${numProperties} propert[y|ies]`}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
