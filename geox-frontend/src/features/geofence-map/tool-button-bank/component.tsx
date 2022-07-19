import { useEditableMode } from "./hooks";
import { MODES } from "./modes";
import { BsArrowsMove } from "react-icons/bs";
import { TbLasso } from "react-icons/tb";
import { RiCursorLine } from "react-icons/ri";
import { FaDrawPolygon } from "react-icons/fa";
import { useTooltip } from "../../../hooks/use-tooltip";
import ReactTooltip from "react-tooltip";
import { BiCart } from "react-icons/bi";
import { MdOutlineDraw, MdOutlineEditRoad } from "react-icons/md";
import { useEffect } from "react";

export const ToolButtonBank = () => {
  const { editableMode, setEditableMode } = useEditableMode();
  const buttonCss =
    "bg-slate-600 hover:bg-blue-500 text-white font-semibold hover:text-white py-2 px-4 border border-blue-500 hover:border-transparent";
  const { tooltip, tooltipEvents } = useTooltip();

  const modes = [
    {
      name: "View",
      icon: <RiCursorLine />,
      onClick: () => setEditableMode(MODES.ViewMode),
      dataTip: "Read-only view of existing geofences",
      active: editableMode === MODES.ViewMode,
    },
    {
      name: "Edit",
      icon: <FaDrawPolygon />,
      onClick: () => setEditableMode(MODES.EditMode),
      dataTip: "Draw new or edit existing geofences",
      active: editableMode === MODES.EditMode,
    },
    {
      name: "Lasso",
      icon: <MdOutlineEditRoad />,
      onClick: () => setEditableMode(MODES.LassoMode),
      dataTip: "Select a group of elements for editing",
      active: editableMode === MODES.LassoMode,
    },
    {
      name: "Polygon Lasso",
      icon: <TbLasso />,
      onClick: () => setEditableMode(MODES.LassoDrawMode),
      dataTip: "Freely draw a polygon",
      active: editableMode === MODES.LassoDrawMode,
    },
    {
      name: "Translate",
      icon: <BsArrowsMove />,
      onClick: () => setEditableMode(MODES.TranslateMode),
      dataTip: "Moves an existing shape",
      active: editableMode === MODES.TranslateMode,
    },
    {
      name: "Polygon from Route",
      icon: <MdOutlineDraw />,
      onClick: () => setEditableMode(MODES.DrawPolygonFromRouteMode),
      dataTip: "Draws a polygon from a route",
      active: editableMode === MODES.DrawPolygonFromRouteMode,
    },
  ];

  useEffect(() => {
    if (window.location.hash === "#ic-demo") {
      setEditableMode(MODES.InstacartDemoMode);
    }
  }, []);

  if (window.location.hash === "#ic-demo") {
    modes.push({
      name: "Instacart demo",
      icon: <BiCart />,
      onClick: () => setEditableMode(MODES.InstacartDemoMode),
      dataTip: "Prop 22 - Instacart demo",
      active: editableMode === MODES.InstacartDemoMode,
    });
  }

  return (
    <div className="grid grid-flow-row gap-0">
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
