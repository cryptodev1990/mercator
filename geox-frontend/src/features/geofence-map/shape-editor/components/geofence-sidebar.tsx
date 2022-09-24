import { useEffect, useState } from "react";

import { MdOutlineArrowBackIos } from "react-icons/md";
import { Tabs } from "./tabs";
import { ShapeEditor } from "./shape-editor";
import { Transition } from "react-transition-group";
import { useShapes } from "../../hooks/use-shapes";
import Loading from "react-loading";
import { ShapeBarPaginator } from "./ShapeBarPaginator";

const ArrowBox = ({ handleClick }: { handleClick: any }) => {
  return (
    <div
      onClick={(e) => handleClick(e)}
      className={
        "flex z-10 bg-slate-600 mx-5 p-1 justify-center cursor-pointer items-center h-fit w-fit"
      }
    >
      <MdOutlineArrowBackIos size={15} />
    </div>
  );
};

const GeofenceSidebar = () => {
  const { shapeForMetadataEdit, isLoading } = useShapes();

  return (
    <GeofenceSidebarView>
      {!isLoading && (
        <Tabs
          children={[<ShapeBarPaginator />, <ShapeEditor />].map((x, i) => (
            <div key={i}>{x}</div>
          ))}
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
            className="w-[300px] z-10 overflow-y-none snap-y bg-gradient-to-br from-slate-600 to-slate-700"
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
