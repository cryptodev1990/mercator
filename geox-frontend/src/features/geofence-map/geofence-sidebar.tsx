import { useState } from "react";

import { MdOutlineArrowBackIos } from "react-icons/md";
import { GetAllShapesRequestType } from "../../client";
import { useGetAllShapesQuery } from "./hooks/openapi-hooks";
import { ShapeCard } from "./shape-card";

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
          <div className="p-5 bg-slate-600">
            <p>
              Welcome to{" "}
              <strong
                className="
                  bg-gradient-to-r bg-clip-text  text-transparent 
                  from-white via-porsche to-white
                  animate-text"
              >
                Geofencer
              </strong>
              ! You're part of our private beta.
            </p>
            <br />
            <p>
              Start adding polygons by clicking on the button bank on the right
            </p>
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
