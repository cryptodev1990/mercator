import { useEffect, useRef, useState } from "react";
import { BiCaretLeft } from "react-icons/bi";
import Dropdown from "../../../common/components/dropdown";
import { CancelIcon } from "../../../common/components/icons";
import { EditorMode } from "../cursor-modes";
import { useCursorMode } from "../hooks/use-cursor-mode";
import { DocsButton } from "./docs-iframe";
import { ToolButtonBank } from "./tool-button-bank/tool-button-bank";

const GuideBar = () => {
  const [hide, setHide] = useState(true);
  const { cursorMode } = useCursorMode();
  const ref = useRef<HTMLButtonElement>(null);

  // Keep track of state in localStorage
  useEffect(() => {
    const hide = localStorage.getItem("guidebar-hide");
    if (hide) {
      setHide(true);
    }
    if (!hide) {
      setHide(false);
    }
  }, []);

  const toggleHide = () => {
    if (hide) {
      localStorage.removeItem("guidebar-hide");
    } else {
      localStorage.setItem("guidebar-hide", "true");
    }
    setHide(!hide);
  };

  const unhideBtn = (
    <button
      ref={ref}
      className="btn btn-xs bg-blue-500 text-white mr-3"
      onClick={toggleHide}
    >
      <BiCaretLeft />
    </button>
  );

  const helpText = {
    [EditorMode.ViewMode]: "Click a shape to edit or right-click to draw",
    [EditorMode.EditMode]:
      "Click to add points, double-click to finish (ESC to cancel)",
    [EditorMode.ModifyMode]: "Drag or delete a point (ESC to cancel)",
    [EditorMode.SplitMode]: "Click through a shape to split it",
    [EditorMode.LassoDrawMode]: "Click and drag to draw",
  };
  // @ts-ignore
  let helpTextForMode = helpText[cursorMode];

  const tipbar = (
    <div>
      <div className="bg-blue-500 w-[320px] px-2 py-1 mr-3 text-sm rounded flex flex-row">
        <p>{helpTextForMode}</p>
        <CancelIcon
          className="hover:cursor-pointer text-white flex-none ml-auto"
          size={16}
          onClick={toggleHide}
        />
      </div>
    </div>
  );

  return <div className="pointer-events-auto">{hide ? unhideBtn : tipbar}</div>;
};

export const TopRightCornerBank = () => {
  return (
    <div className="z-10 mx-2 flex flex-col h-screen space-y-3 items-end pointer-events-none">
      <div className="flex flex-row">
        <GuideBar />
        <div className="pointer-events-auto">
          <Dropdown />
        </div>
      </div>
      <div className="pointer-events-auto">
        <ToolButtonBank />
      </div>
      <div className="pointer-events-auto">
        <DocsButton />
      </div>
    </div>
  );
};
