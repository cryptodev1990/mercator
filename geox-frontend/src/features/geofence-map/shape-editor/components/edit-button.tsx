import { BsPencil } from "react-icons/bs";
import { GeoShape } from "../../../../client";
import { useShapes } from "../../hooks/use-shapes";

export const MetadataEditButton = ({ shape }: { shape: GeoShape }) => {
  const { setShapeForMetadataEdit } = useShapes();
  if (!shape.uuid || shape.uuid === undefined) {
    return null;
  }
  return (
    <button
      className="btn btn-square btn-sm bg-slate-700 hover:bg-blue-400 hover:border-blue-400"
      title="Edit metadata"
      onClick={() => setShapeForMetadataEdit(shape)}
    >
      <BsPencil className="fill-white" />
    </button>
  );
};
