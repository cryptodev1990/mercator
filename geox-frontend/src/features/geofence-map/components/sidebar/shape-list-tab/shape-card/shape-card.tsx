import Loading from "react-loading";
import { MetadataEditButton } from "./edit-button";
import simplur from "simplur";

import toast from "react-hot-toast";
import {
  TargetIcon,
  DeleteIcon,
} from "../../../../../../common/components/icons";
import { useViewport } from "../../../../hooks/use-viewport";
import { useCursorMode } from "../../../../hooks/use-cursor-mode";
import { EditorMode } from "../../../../cursor-modes";
import { GeoShapeMetadata } from "../../../../../../client/models/GeoShapeMetadata";
import { useSelectedShapes } from "../../../../hooks/use-selected-shapes";
import { useShapes } from "../../../../hooks/use-shapes";
import { EditableLabel } from "../../../../../../common/components/editable-label";
import { DragHandle } from "./drag-handle";
import { SHAPE_CARD_IMAGE } from "./drag-images";
import React, { useContext } from "react";
import { UIContext } from "../../../../contexts/ui-context";

export const ShapeCard = ({
  shape,
  onMouseEnter,
  onMouseLeave,
  isHovered,
}: {
  shape: GeoShapeMetadata;
  onMouseEnter: (e: React.MouseEvent) => void;
  onMouseLeave: (e: React.MouseEvent) => void;
  isHovered: boolean;
}) => {
  const {
    deleteShapes,
    updateLoading,
    clearSelectedFeatureIndexes,
    updateShape,
  } = useShapes();

  const { confirmDelete, setHeading } = useContext(UIContext);

  const { selectedFeatureCollection } = useSelectedShapes();

  const { isSelected, selectedDataIsLoading, clearSelectedShapeUuids } =
    useSelectedShapes();
  const { setCursorMode } = useCursorMode();
  const { snapToBounds } = useViewport();

  const selectionBg = isSelected(shape) ? "text-blue-800" : "text-white";
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
        <DragHandle
          shape={shape}
          dragImage={SHAPE_CARD_IMAGE}
          // dataTip={`Drag into ${shape.name} another folder`}
        />
        <EditableLabel
          value={shape?.name || "New shape"}
          disabled={selectedDataIsLoading}
          onChange={(newName) => {
            const geojson = selectedFeatureCollection?.features.find(
              (x) => x?.properties?.__uuid === shape.uuid
            );

            if (!geojson) {
              console.error("Could not find geojson for shape", shape);
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
        />
        <div
          className={`transition flex flex-row justify-start space-x-1 ${selectionOpacity} ml-auto`}
        >
          {isHovered && (
            <>
              <MetadataEditButton shape={shape} />
              <button
                className="cx-btn-square hover:bg-red-400 hover:border-red-400 box-border"
                disabled={updateLoading}
                onClick={(e: any) => {
                  setHeading("Delete geofence?");
                  if (!shape.uuid) toast.error("Delete shape failed");
                  else {
                    const coords = [e.clientX, e.clientY];
                    confirmDelete(coords, () => {
                      deleteShapes([shape.uuid]);
                      clearSelectedShapeUuids();
                      clearSelectedFeatureIndexes();
                      setCursorMode(EditorMode.ViewMode);
                    });
                  }
                }}
              >
                {updateLoading ? (
                  <Loading height={8} width={8} />
                ) : (
                  <DeleteIcon className="fill-white" />
                )}
              </button>
              <button
                className="cx-btn-square hover:bg-green-400 hover:border-green-400 box-border"
                data-tip="Zoom to"
                disabled={selectedDataIsLoading}
                onClick={() => {
                  snapToBounds({ category: "selected" });
                }}
              >
                <TargetIcon
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
            <div
              className="
              whitespace-nowrap
            text-xs
            font-sans
            tracking-tight text-white box-border select-none overflow-none text-ellipsis"
            >
              {simplur`${numProperties} propert[y|ies]`}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
