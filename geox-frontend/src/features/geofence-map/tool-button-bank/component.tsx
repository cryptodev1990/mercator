// @ts-ignore
import { useCursorMode } from "../hooks/use-cursor-mode";

import { EditorMode } from "../cursor-modes";
import { BsArrowsMove, BsScissors } from "react-icons/bs";
import { TbLasso } from "react-icons/tb";
import { CgEditMarkup } from "react-icons/cg";
import { RiCursorLine } from "react-icons/ri";
import { FaDrawPolygon } from "react-icons/fa";
import { useTooltip } from "../../../hooks/use-tooltip";
import ReactTooltip from "react-tooltip";
import { BiCart } from "react-icons/bi";
import { MdOutlineDraw, MdOutlineEditRoad } from "react-icons/md";
import { useEffect } from "react";
import { useShapes } from "../hooks/use-shapes";

export const ToolButtonBank = () => {
  const { cursorMode, setCursorMode } = useCursorMode();
  const { tooltip, tooltipEvents } = useTooltip();
  const { getNumSelectedShapes } = useShapes();

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
    {
      name: "Lasso",
      icon: <MdOutlineEditRoad />,
      onClick: () => setCursorMode(EditorMode.LassoMode),
      dataTip: "Select a group of elements for editing",
      active: cursorMode === EditorMode.LassoMode,
    },
    {
      name: "Polygon Lasso",
      icon: <TbLasso />,
      onClick: () => setCursorMode(EditorMode.LassoDrawMode),
      dataTip: "Freely draw a polygon",
      active: cursorMode === EditorMode.LassoDrawMode,
    },
    {
      name: "Translate",
      icon: <BsArrowsMove />,
      onClick: () => setCursorMode(EditorMode.TranslateMode),
      dataTip: "Moves an existing shape",
      active: cursorMode === EditorMode.TranslateMode,
    },
    {
      name: "Polygon from Route",
      icon: <MdOutlineDraw />,
      onClick: () => setCursorMode(EditorMode.DrawPolygonFromRouteMode),
      dataTip: "Draws a polygon from a route",
      active: cursorMode === EditorMode.DrawPolygonFromRouteMode,
    },
    {
      name: "Alter",
      icon: <CgEditMarkup />,
      onClick: () => setCursorMode(EditorMode.ModifyMode),
      dataTip: "Alter points on existing shape",
      active: cursorMode === EditorMode.ModifyMode,
      disabled: getNumSelectedShapes() !== 1,
    },
    {
      name: "Split existing shape",
      icon: <BsScissors />,
      onClick: () => setCursorMode(EditorMode.SplitMode),
      dataTip: "Split existing shape",
      active: cursorMode === EditorMode.SplitMode,
      disabled: getNumSelectedShapes() !== 1,
    },
  ];

  useEffect(() => {
    if (window.location.hash === "#ic-demo") {
      setCursorMode(EditorMode.InstacartDemoMode);
    }
  }, []);

  if (window.location.hash === "#ic-demo") {
    modes.push({
      name: "Instacart demo",
      icon: <BiCart />,
      onClick: () => setCursorMode(EditorMode.InstacartDemoMode),
      dataTip: "Prop 22 - Instacart demo",
      active: cursorMode === EditorMode.InstacartDemoMode,
    });
  }
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
            data-tip={mode.dataTip}
            key={mode.name}
            disabled={mode.disabled}
            onClick={mode.onClick}
            className={classes}
            {...tooltipEvents}
          >
            {mode.icon}
          </button>
        );
      })}
      {tooltip && <ReactTooltip effect="solid" place="left" type="dark" />}
    </div>
  );
};
