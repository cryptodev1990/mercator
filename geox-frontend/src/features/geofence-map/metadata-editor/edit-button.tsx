import { BsPencil } from "react-icons/bs";
import { GeoShape } from "../../../client";
import { Button } from "../../../components/button";
import { useEditModal } from "./hooks";

export const MetadataEditButton = ({ shape }: { shape: GeoShape }) => {
  const { setShapeForEdit } = useEditModal();
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
