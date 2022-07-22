import { useEffect, useState } from "react";

import { MdOutlineArrowBackIos } from "react-icons/md";
import { GetAllShapesRequestType } from "../../../client";
import { Tabs } from "./tabs";
import { useGetAllShapesQuery } from "../hooks/openapi-hooks";
import { ShapeEditor } from "./shape-editor";
import { useEditableShape } from "./hooks";
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

export const GeofenceSidebar = () => {
  const [hidden, setHidden] = useState(false);
  const { data: shapes } = useGetAllShapesQuery(GetAllShapesRequestType.DOMAIN);

  // Feature: Hide sidebar with shortkey
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

  const { shapeForEdit } = useEditableShape();

  // Feature: Display card for each shape in the namespace
  const shapeCards = shapes?.map((shape, i) => (
    <ShapeCard shape={shape} key={i} />
  ));

  return (
    <GeofenceSidebarView hidden={hidden} setHidden={setHidden}>
      <Tabs
        children={[
          shapes?.length !== 0 ? <div>{shapeCards}</div> : <NewUserMessage />,
          <ShapeEditor />,
        ]}
        active={shapeForEdit ? 1 : 0}
        tabnames={["🌐", "📙"]}
      />
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
