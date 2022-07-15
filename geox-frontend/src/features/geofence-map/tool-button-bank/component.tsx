import { MdEdit } from "react-icons/md";
import { useEditableMode } from "./hooks";
import { MODES } from "./modes";
import { BsArrowsMove, BsSquare } from "react-icons/bs";
import { TbLasso } from "react-icons/tb";
import { useTooltip } from "../../../hooks/use-tooltip";
import ReactTooltip from "react-tooltip";

export const ToolButtonBank = () => {
  const { editableMode, setEditableMode } = useEditableMode();
  const buttonCss =
    "bg-slate-600 hover:bg-blue-500 text-white font-semibold hover:text-white py-2 px-4 border border-blue-500 hover:border-transparent";
  const { tooltip, tooltipEvents } = useTooltip();

  const modes = [
    {
      name: "View",
      icon: <BsSquare />,
      onClick: () => setEditableMode(MODES.ViewMode),
      dataTip: "Read-only view of existing geofences",
      active: editableMode === MODES.ViewMode,
    },
    {
      name: "Edit",
      icon: <MdEdit />,
      onClick: () => setEditableMode(MODES.EditMode),
      dataTip: "Draw new or edit existing geofences",
      active: editableMode === MODES.EditMode,
    },
    {
      name: "Lasso",
      icon: <TbLasso />,
      onClick: () => setEditableMode(MODES.LassoMode),
      dataTip: "Select a group of elements for editing",
      active: editableMode === MODES.LassoMode,
    },
    {
      name: "Translate",
      icon: <BsArrowsMove />,
      onClick: () => setEditableMode(MODES.TranslateMode),
      dataTip: "Moves an existing shape",
      active: editableMode === MODES.TranslateMode,
    },
  ];

  return (
    <div className="grid grid-flow-row gap-0">
      {modes.map((mode) => {
        let classes = buttonCss;
        if (mode.active) {
          classes += " bg-blue-500";
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
