import { BsPencil } from "react-icons/bs";
import { GeoShape } from "../../../../client";
import { Button } from "../../../../common/components/button";
// @ts-ignore
import { useEditableShape } from "../hooks";

export const MetadataEditButton = ({ shape }: { shape: GeoShape }) => {
  const { setShapeForEdit } = useEditableShape();
  return (
    <Button
      onClick={() => {
        setShapeForEdit(shape);
      }}
    >
      <span className="mx-1">Edit</span>
      <BsPencil />
    </Button>
  );
};
