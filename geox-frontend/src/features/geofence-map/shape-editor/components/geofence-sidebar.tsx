import { useEffect, useState } from "react";

import { MdOutlineArrowBackIos } from "react-icons/md";
import { Tabs } from "./tabs";
import { ShapeEditor } from "./shape-editor";
import { ShapeCard } from "./shape-card";
import { Transition } from "react-transition-group";
import { useShapes } from "../../hooks/use-shapes";
import Loading from "react-loading";

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

const ArrowBox = ({ handleClick }: { handleClick: any }) => {
  return (
    <div
      onClick={(e) => handleClick(e)}
      className={
        "flex z-30 bg-slate-600 mx-5 p-1 justify-center cursor-pointer items-center h-fit w-fit"
      }
    >
      <MdOutlineArrowBackIos size={15} />
    </div>
  );
};

const GeofenceSidebar = () => {
  const { shapes, shapeForMetadataEdit, isLoading } = useShapes();

  // Feature: Display card for each shape in the namespace
  const shapeCards = shapes?.map((shape, i) => (
    <ShapeCard shape={shape} key={i} />
  ));

  return (
    <GeofenceSidebarView>
      {!isLoading && (
        <Tabs
          children={[
            shapes?.length !== 0 ? (
              <div key={0} className="overflow-y-scroll">
                {shapeCards}
              </div>
            ) : (
              <div key={0}>
                <NewUserMessage />
              </div>
            ),
            <div key={1}>
              <ShapeEditor />
            </div>,
          ]}
          active={shapeForMetadataEdit ? 1 : 0}
          tabnames={["Shapes", "Metadata Editor"]}
        />
      )}
      {isLoading && (
        <div className="w-max m-auto">
          <Loading type="bubbles" />
        </div>
      )}
    </GeofenceSidebarView>
  );
};

const GeofenceSidebarView = ({ children }: { children: any }) => {
  const [hidden, setHidden] = useState(false);

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

  const defaultStyles = {
    zIndex: "40",
    transform: "translateX(0px)",
    transition: "transform 200ms",
  };

  const transitionStyles: any = {
    entering: { transform: "translateX(0px)" },
    entered: { transform: "translateX(0px)" },
    exiting: { transform: "translateX(0px)" },
    exited: { transform: "translateX(-500%)" },
  };

  const arrowTransitionStyles: any = {
    entering: { transform: "rotate(180deg)" },
    entered: { transform: "rotate(-180deg)" },
    exiting: { transform: "translateX(0px)" },
    exited: { transform: "translateX(-500%)" },
  };

  return (
    <>
      <Transition in={!hidden} timeout={50}>
        {(state: any) => (
          <div
            className="w-[300px] z-30 overflow-y-none snap-y bg-gradient-to-br from-slate-600 to-slate-700"
            style={{
              ...defaultStyles,
              ...transitionStyles[state],
            }}
          >
            {children}
          </div>
        )}
      </Transition>

      <Transition in={!hidden} timeout={50}>
        {(state: any) => (
          <div
            style={{
              height: "23px",
              ...defaultStyles,
              ...arrowTransitionStyles[state],
            }}
          >
            <ArrowBox handleClick={() => setHidden((isHidden) => !hidden)} />
          </div>
        )}
      </Transition>
    </>
  );
};

export { GeofenceSidebar };
