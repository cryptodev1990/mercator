import { MdDelete } from "react-icons/md";
import Loading from "react-loading";
import { useUpdateShapeMutation } from "../../hooks/openapi-hooks";
import { MetadataEditButton } from "./edit-button";
import simplur from "simplur";

import toast from "react-hot-toast";
import { TbTarget } from "react-icons/tb";
import { useViewport } from "../../hooks/use-viewport";
import { useCursorMode } from "../../hooks/use-cursor-mode";
import { EditorMode } from "../../cursor-modes";
import { GeoShapeMetadata } from "../../../../client/models/GeoShapeMetadata";
import { useState } from "react";
import { useSelectedShapes } from "../../hooks/use-selected-shapes";

export const ShapeCard = ({ shape }: { shape: GeoShapeMetadata }) => {
  const { mutate: updateShape, isLoading } = useUpdateShapeMutation();

  const {
    isSelected,
    selectOneShapeUuid,
    removeSelectedShapeUuid,
    selectedDataIsLoading,
  } = useSelectedShapes();

  const [isHovered, setIsHovered] = useState(false);

  const { setCursorMode } = useCursorMode();
  const { snapToBounds } = useViewport();

  const selectionBg = isSelected(shape) ? "bg-slate-600" : "bg-slate-800";
  const selectionOpacity = isSelected(shape) ? "opacity-100" : "opacity-50";
  const numProperties = Object.keys(shape.properties).filter(
    (x) => !x.startsWith("__")
  ).length;
  return (
    <div
      onMouseEnter={() => {
        selectOneShapeUuid(shape.uuid);
        setIsHovered(true);
      }}
      onMouseLeave={() => {
        removeSelectedShapeUuid(shape.uuid);
        setIsHovered(false);
      }}
      className={`p-3 max-w-sm relative border-b border-b-slate-600 snap-start bg-slate-600 border-gray-200 ${selectionBg}`}
    >
      <div className="flex flex-row justify-between items-center">
        <h5
          title={shape?.properties?.name}
          className="text-1xl font-sans tracking-tight text-white truncate"
        >
          {shape?.properties?.name || "New geofence"}
        </h5>
        <div
          className={`transition flex flex-row justify-start space-x-1 ${selectionOpacity}`}
        >
          {isHovered && (
            <>
              <MetadataEditButton shape={shape} />
              <button
                className="btn btn-square btn-sm bg-slate-700 hover:bg-red-400 hover:border-red-400"
                title="Delete"
                onClick={() => {
                  if (!shape.uuid) toast.error("Delete shape failed");
                  else {
                    updateShape({ uuid: shape.uuid, should_delete: true });
                    setCursorMode(EditorMode.ViewMode);
                  }
                }}
              >
                {isLoading ? (
                  <Loading height={8} width={8} />
                ) : (
                  <MdDelete className="fill-white" />
                )}
              </button>
              <button
                className="btn btn-square btn-sm bg-slate-700 hover:bg-green-400 hover:border-green-400"
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
            <div className="flex flex-row justify-center items-center">
              <div className="text-xs font-sans tracking-tight text-white">
                {simplur`${numProperties} propert[y|ies]`}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
