import { MdDelete } from "react-icons/md";
import Loading from "react-loading";
import { useUpdateShapeMutation } from "../../hooks/openapi-hooks";
import { MetadataEditButton } from "./edit-button";
import { useShapes } from "../../hooks/use-shapes";
import { GeoShape } from "../../../../client";
import toast from "react-hot-toast";
import { TbTarget } from "react-icons/tb";
import { useViewport } from "../../hooks/use-viewport";
import { useCursorMode } from "../../hooks/use-cursor-mode";
import { EditorMode } from "../../cursor-modes";

export const ShapeCard = ({ shape }: { shape: GeoShape }) => {
  const { mutate: updateShape, isLoading } = useUpdateShapeMutation();
  const { selectOneShapeUuid, removeSelectedShapeUuid, shapeIsSelected } =
    useShapes();

  const { setCursorMode } = useCursorMode();
  const { snapToBounds } = useViewport();
  if (!shape.uuid || shape.uuid === undefined) {
    return null;
  }
  const selectionBg = shapeIsSelected(shape) ? "bg-slate-600" : "bg-slate-800";
  const selectionOpacity = shapeIsSelected(shape)
    ? "opacity-100"
    : "opacity-50";
  return (
    <div
      onMouseEnter={() => selectOneShapeUuid(shape.uuid ?? "")}
      onMouseLeave={() => removeSelectedShapeUuid(shape.uuid ?? "")}
      className={`p-3 max-w-sm relative border-b border-b-slate-600 snap-start bg-slate-600 border-gray-200 ${selectionBg}`}
    >
      <div className="flex flex-row justify-between items-center">
        <h5
          title={shape?.geojson?.properties?.name}
          className="text-1xl font-sans tracking-tight text-white truncate"
        >
          {shape?.geojson?.properties?.name || "New geofence"}
        </h5>
        <div
          className={`transition flex flex-row justify-start space-x-1 ${selectionOpacity}`}
        >
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
            onClick={() => {
              snapToBounds({ category: "selected" });
            }}
          >
            <TbTarget className="fill-white" />
          </button>
        </div>
      </div>
    </div>
  );
};
