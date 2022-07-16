import { useEffect, useState } from "react";

import { MdOutlineArrowBackIos } from "react-icons/md";
import { GetAllShapesRequestType } from "../../client";
import { useGetAllShapesQuery } from "./hooks/openapi-hooks";
import { ShapeCard } from "./shape-card";

const NewUserMessage = () => {
  return (
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
      <p>Start adding polygons by clicking on the button bank on the right</p>
    </div>
  );
};

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

export const GeofenceSidebar = () => {
  const [hidden, setHidden] = useState(false);
  const { data: shapes } = useGetAllShapesQuery(GetAllShapesRequestType.DOMAIN);

  useEffect(() => {
    async function shortkey(event: KeyboardEvent) {
      if (event.ctrlKey && event.key === "b") {
        setHidden((oldState) => !oldState);
      }
    }

    document.body.addEventListener("keydown", shortkey, false);

    return () => {
      document.body.removeEventListener("keydown", shortkey, false);
    };
  }, []);

  if (shapes?.length === 0) {
    return (
      <GeofenceSidebarView hidden={hidden} setHidden={setHidden}>
        <NewUserMessage />;
      </GeofenceSidebarView>
    );
  }

  const shapeCards = shapes
    ?.sort((a, b) => toUnix(a.created_at) - toUnix(b.created_at))
    .map((shape) => <ShapeCard shape={shape} />);

  return (
    <GeofenceSidebarView hidden={hidden} setHidden={setHidden}>
      {shapeCards}
    </GeofenceSidebarView>
  );
};

const GeofenceSidebarView = ({
  children,
  hidden,
  setHidden,
}: {
  children: any;
  hidden: any;
  setHidden: any;
}) => {
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
        {children}
      </div>
      <ArrowBox
        handleClick={() => setHidden(true)}
        additionalClasses="rotate-0"
      />
    </>
  );
};
