import { useEffect, useState } from "react";
import { OutlineArrowForwardIcon } from "../../../../common/components/icons";
import { Transition } from "react-transition-group";

const ArrowBox = ({ handleClick }: { handleClick: any }) => {
  return (
    <div
      onClick={(e) => handleClick(e)}
      className={
        "flex z-10 bg-slate-600 mx-5 p-1 justify-center cursor-pointer items-center h-fit w-fit"
      }
    >
      <OutlineArrowForwardIcon size={15} />
    </div>
  );
};

export const SidebarDrawer = ({ children }: { children: any }) => {
  /**
   * Handles showing / hiding the sidebar
   */
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
            className={`w-[300px] z-10 bg-slate-700 overflow-y-scroll scrollbar-thin`}
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
