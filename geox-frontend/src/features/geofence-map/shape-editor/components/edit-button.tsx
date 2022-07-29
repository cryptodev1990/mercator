import { BsPencil } from "react-icons/bs";
import { GeoShape } from "../../../../client";
import { Button } from "../../../../common/components/button";
import { useShapes } from "../../hooks/use-shapes";

export const MetadataEditButton = ({ shape }: { shape: GeoShape }) => {
  const { setShapeForMetadataEdit } = useShapes();
  if (!shape.uuid || shape.uuid === undefined) {
    return null;
  }
  return (
    <Button onClick={() => setShapeForMetadataEdit(shape)}>
      <span className="mx-1">Edit</span>
      <BsPencil />
    </Button>
  );
};
