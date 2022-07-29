import { MdDelete } from "react-icons/md";
import Loading from "react-loading";
import { Button } from "../../../../common/components/button";
import { useUpdateShapeMutation } from "../../hooks/openapi-hooks";
import { MetadataEditButton } from "./edit-button";
import { useShapes } from "../../hooks/use-shapes";
import { GeoShape } from "../../../../client";

export const ShapeCard = ({ shape }: { shape: GeoShape }) => {
  const { mutate: updateShape, isLoading } = useUpdateShapeMutation();
  const { addSelectedShapeUuid, removeSelectedShapeUuid, shapeIsSelected } =
    useShapes();
  if (!shape.uuid || shape.uuid === undefined) {
    return null;
  }
  const selectionBg = shapeIsSelected(shape) ? "bg-slate-600" : "bg-slate-800";
  return (
    <div
      onMouseOver={() => addSelectedShapeUuid(shape.uuid ?? "")}
      onMouseLeave={() => removeSelectedShapeUuid(shape.uuid ?? "")}
      className={`p-6 max-w-sm relative snap-start bg-slate-600 first-child:rounded-none last-child:rounded-none rounded-lg border border-gray-200 shadow-md ${selectionBg}`}
    >
      <h5 className="mb-2 text-2xl font-bold tracking-tight text-white">
        {shape?.geojson?.properties?.name || "New geofence"}
      </h5>
      <div className="flex flex-row justify-start space-x-2">
        <MetadataEditButton shape={shape} />
        <Button
          onClick={() => {
            if (!shape.uuid) alert("TODO Delete shape failed");
            else updateShape({ uuid: shape.uuid, should_delete: true });
          }}
        >
          <span className="mx-1">Delete</span>
          {isLoading ? <Loading height={8} width={8} /> : <MdDelete />}
        </Button>
      </div>
    </div>
  );
};
