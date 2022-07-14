import { useEffect, useState } from "react";
import { BsPencil } from "react-icons/bs";

import { MdDelete, MdOutlineArrowBackIos } from "react-icons/md";
import Loading from "react-loading";
import { GeoShape, GetAllShapesRequestType } from "../../client";
import { EditModal } from "../edit-modal";
import {
  useGetAllShapesQuery,
  useSelectedShapes,
  useUpdateShapeMutation,
} from "./hooks";
import { useEditModal } from "./hooks/ui-hooks";

const ArrowBox = ({
  handleClick,
  additionalClasses = "",
}: {
  handleClick: any;
  additionalClasses: string;
}) => {
  return (
    <div
      onClick={(e) => handleClick(e)}
      className={
        "flex z-30 bg-slate-600 mx-5 justify-center cursor-pointer items-center h-fit w-fit " +
        additionalClasses
      }
    >
      <MdOutlineArrowBackIos size={30} />
    </div>
  );
};

const Button = (props: any) => {
  const { children, ...rest } = props;
  return (
    <button
      {...rest}
      className="inline-flex items-center py-2 px-3 text-sm font-medium text-center text-white bg-blue-700 rounded-lg hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
    >
      {props.children ? props.children : "Save"}
    </button>
  );
};

const ShapeCard = ({ shape }: { shape: GeoShape }) => {
  const { mutate: updateShape, isLoading } = useUpdateShapeMutation();
  const { selectOne, removeAllSelections, isSelected } = useSelectedShapes();
  const { shapeForEdit, setShapeForEdit } = useEditModal();
  const selectionBg = isSelected(shape.uuid) ? "bg-slate-600" : "bg-slate-800";
  return (
    <div
      onMouseOver={() => {
        console.log(shape.uuid + " selected");
        selectOne(shape);
      }}
      onMouseLeave={() => {
        removeAllSelections();
      }}
      className={`p-6 max-w-sm relative snap-start bg-slate-600 rounded-lg border border-gray-200 shadow-md ${selectionBg}`}
      style={{}}
    >
      <h5 className="mb-2 text-2xl font-bold tracking-tight text-white">
        {shape.name}
      </h5>
      <div className="flex flex-row justify-start space-x-2">
        <Button
          onClick={() => {
            setShapeForEdit(shape);
          }}
        >
          <span className="mx-1">Edit</span>
          <BsPencil />
        </Button>
        <Button
          onClick={() => updateShape({ uuid: shape.uuid, should_delete: true })}
        >
          <span className="mx-1">Delete</span>
          {isLoading ? <Loading height={8} width={8} /> : <MdDelete />}
        </Button>
      </div>
    </div>
  );
};

const toUnix = (dt: string) => Math.floor(new Date(dt).getTime() / 1000);

const GeofenceSidebar = () => {
  const [hidden, setHidden] = useState(false);
  const { data: shapes } = useGetAllShapesQuery(GetAllShapesRequestType.DOMAIN);

  if (hidden) {
    return (
      <ArrowBox
        handleClick={() => setHidden(false)}
        additionalClasses={"rotate-180"}
      />
    );
  }

  return (
    <>
      <div className="bg-slate-600 w-[300px] z-30 overflow-y-scroll snap-y">
        {shapes
          ?.sort((a, b) => toUnix(a.created_at) - toUnix(b.created_at))
          .map((shape) => (
            <ShapeCard shape={shape} />
          ))}
        {shapes?.length === 0 && (
          <div className="p-5">
            Start adding polygons by clicking on the map.
          </div>
        )}
      </div>
      <ArrowBox
        handleClick={() => setHidden(true)}
        additionalClasses="rotate-0"
      />
    </>
  );
};

export { GeofenceSidebar };
