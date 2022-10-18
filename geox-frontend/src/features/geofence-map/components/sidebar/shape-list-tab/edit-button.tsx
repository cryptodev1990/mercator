import { BsPencil } from "react-icons/bs";
import { GeoShapeMetadata } from "../../../../../client/models/GeoShapeMetadata";
import { useShapes } from "../../../hooks/use-shapes";

export const MetadataEditButton = ({ shape }: { shape: GeoShapeMetadata }) => {
  const { setShapeForPropertyEdit } = useShapes();
  return (
    <button
      className="btn btn-square btn-sm bg-slate-700 hover:bg-blue-400 hover:border-blue-400 box-border"
      title="Edit metadata"
      onClick={() => setShapeForPropertyEdit(shape)}
    >
      <BsPencil className="fill-white" />
    </button>
  );
};
