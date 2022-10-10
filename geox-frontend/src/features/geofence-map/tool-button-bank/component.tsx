// @ts-ignore
import { useCursorMode } from "../hooks/use-cursor-mode";

import { EditorMode } from "../cursor-modes";
import { BsScissors } from "react-icons/bs";
import { TbLasso } from "react-icons/tb";
import { CgEditMarkup } from "react-icons/cg";
import { RiCursorLine } from "react-icons/ri";
import { FaDrawPolygon } from "react-icons/fa";
import { useSelectedShapes } from "../hooks/use-selected-shapes";

export const ToolButtonBank = () => {
  const { cursorMode, setCursorMode } = useCursorMode();
  const { numSelected } = useSelectedShapes();

  const modes = [
    {
      name: "View",
      icon: <RiCursorLine />,
      onClick: () => setCursorMode(EditorMode.ViewMode),
      dataTip: "Read-only view of existing geofences",
      active: cursorMode === EditorMode.ViewMode,
    },
    {
      name: "Edit",
      icon: <FaDrawPolygon />,
      onClick: () => setCursorMode(EditorMode.EditMode),
      dataTip: "Draw new or edit existing geofences",
      active: cursorMode === EditorMode.EditMode,
    },
    // {
    //   name: "Lasso",
    //   icon: <MdOutlineEditRoad />,
    //   onClick: () => setCursorMode(EditorMode.LassoMode),
    //   dataTip: "Select a group of elements for editing",
    //   active: cursorMode === EditorMode.LassoMode,
    // },
    {
      name: "Polygon Lasso",
      icon: <TbLasso />,
      onClick: () => setCursorMode(EditorMode.LassoDrawMode),
      dataTip: "Freely draw a polygon",
      active: cursorMode === EditorMode.LassoDrawMode,
    },
    // {
    //   name: "Translate",
    //   icon: <BsArrowsMove />,
    //   onClick: () => setCursorMode(EditorMode.TranslateMode),
    //   dataTip: "Coming soon",
    //   disabled: true,
    //   active: cursorMode === EditorMode.TranslateMode,
    // },
    // {
    //   name: "Polygon from Route",
    //   icon: <MdOutlineDraw />,
    //   onClick: () => setCursorMode(EditorMode.DrawPolygonFromRouteMode),
    //   dataTip: "Coming soon",
    //   disabled: true,
    //   active: cursorMode === EditorMode.DrawPolygonFromRouteMode,
    // },
    {
      name: "Alter",
      icon: <CgEditMarkup />,
      onClick: () => setCursorMode(EditorMode.ModifyMode),
      dataTip: "Alter points on existing shape",
      active: cursorMode === EditorMode.ModifyMode,
      disabled: numSelected !== 1,
    },
    {
      name: "Split existing shape",
      icon: <BsScissors />,
      onClick: () => setCursorMode(EditorMode.SplitMode),
      dataTip: "Split existing shape",
      active: cursorMode === EditorMode.SplitMode,
      disabled: numSelected !== 1,
    },
  ];

  const buttonCss =
    "bg-slate-600 hover:bg-blue-500 text-white font-semibold disabled:bg-slate-900 hover:text-white py-2 px-4 border border-blue-500 hover:border-transparent";

  return (
    <div className="grid grid-flow-row gap-0 ">
      {modes.map((mode) => {
        let classes = buttonCss;
        if (mode.active) {
          classes += " bg-blue-500";
        } else if (mode.name === "Instacart demo") {
          classes += " bg-red-700";
        }
        return (
          <button
            // data-tip={mode.dataTip}
            key={mode.name}
            disabled={mode.disabled}
            title={mode.dataTip}
            onClick={mode.onClick}
            className={classes}
          >
            {mode.icon}
          </button>
        );
      })}
    </div>
  );
};
