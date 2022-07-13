import React, { useState } from "react";
import { BsPencil } from "react-icons/bs";

import { MdDelete, MdOutlineArrowBackIos } from "react-icons/md";
import { GeoShape } from "../../client";
import { useGetAllShapesQuery } from "./hooks";

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

const ShapeCard = ({ shape }: { shape: GeoShape }) => {
  return (
    <div className="p-6 max-w-sm snap-start bg-white rounded-lg border border-gray-200 shadow-md dark:bg-gray-800 dark:border-gray-700">
      <h5 className="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
        {shape.name}
      </h5>
      <div className="flex flex-row justify-start space-x-2">
        <button className="inline-flex items-center py-2 px-3 text-sm font-medium text-center text-white bg-blue-700 rounded-lg hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
          <span className="mx-1">Edit</span>
          <BsPencil />
        </button>
        <button className="inline-flex items-center py-2 px-3 text-sm font-medium text-center text-white bg-blue-700 rounded-lg hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
          <span className="mx-1">Delete</span>
          <MdDelete />
        </button>
      </div>
    </div>
  );
};

const toUnix = (dt: string) => Math.floor(new Date(dt).getTime() / 1000);

const GeofenceSidebar = () => {
  const [hidden, setHidden] = useState(false);
  const { data: shapes } = useGetAllShapesQuery();

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
      </div>
      <ArrowBox
        handleClick={() => setHidden(true)}
        additionalClasses="rotate-0"
      />
    </>
  );
};

export { GeofenceSidebar };
