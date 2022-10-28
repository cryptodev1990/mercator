import { PencilIcon } from "../../../../../../common/components/icons";
import { GeoShapeMetadata } from "../../../../../../client/models/GeoShapeMetadata";
import { useShapes } from "../../../../hooks/use-shapes";

export const MetadataEditButton = ({ shape }: { shape: GeoShapeMetadata }) => {
  const { setShapeForPropertyEdit } = useShapes();
  return (
    <button
      className="cx-btn-square bg-slate-700 hover:bg-blue-400 hover:border-blue-400 box-border"
      data-tip="Edit this shape's text metadata"
      onClick={() => setShapeForPropertyEdit(shape)}
    >
      <PencilIcon className="fill-white" />
    </button>
  );
};
