// @ts-ignore
import { useCursorMode } from "../../hooks/use-cursor-mode";

import { EditorMode } from "../../cursor-modes";
import { BsScissors } from "react-icons/bs";
import { TbLasso } from "react-icons/tb";
import { CgEditMarkup } from "react-icons/cg";
import { RiCursorLine } from "react-icons/ri";
import { FaClock, FaDrawPolygon } from "react-icons/fa";
import { useSelectedShapes } from "../../hooks/use-selected-shapes";
import { MdDriveEta } from "react-icons/md";
import { useEffect, useState } from "react";
import { IsochroneControls } from "./isochrone-controls";

export const ToolButtonBank = () => {
  const { cursorMode, setCursorMode } = useCursorMode();
  const { numSelected } = useSelectedShapes();
  const [pushOut, setPushOut] = useState(false);

  const modes = [
    {
      name: "View",
      icon: <RiCursorLine />,
      onClick: () => setCursorMode(EditorMode.ViewMode),
      dataTip: "View-only mode (Esc)",
      active: cursorMode === EditorMode.ViewMode,
    },
    {
      name: "Edit",
      icon: <FaDrawPolygon />,
      onClick: () => setCursorMode(EditorMode.EditMode),
      dataTip: "Draw a shape by clicking",
      active: cursorMode === EditorMode.EditMode,
    },
    {
      name: "Drive time",
      icon: <MdDriveEta />,
      onClick: () => setCursorMode(EditorMode.DrawIsochroneMode),
      dataTip: "Drive time distance",
      active: cursorMode === EditorMode.ModifyMode,
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
      dataTip: "Edit an existing shape",
      active: cursorMode === EditorMode.ModifyMode,
      disabled: numSelected !== 1,
    },
    {
      name: "Split existing shape",
      icon: <BsScissors />,
      onClick: () => setCursorMode(EditorMode.SplitMode),
      dataTip: "Split a selection by drawing through it",
      active: cursorMode === EditorMode.SplitMode,
      disabled: numSelected !== 1,
    },
  ];

  useEffect(() => {
    setPushOut(cursorMode === EditorMode.DrawIsochroneMode);
  }, [cursorMode]);

  const buttonCss =
    "bg-slate-600 hover:bg-blue-500 text-white font-semibold disabled:bg-slate-900 hover:text-white py-2 px-4 border border-blue-500 hover:border-transparent ";

  return (
    <div className="flex flex-col items-end">
      {modes.map((mode) => {
        let classes = buttonCss;
        if (mode.active) {
          classes += " bg-blue-500";
        }
        if (mode.name === "Drive time") {
          return (
            <div className="bg-blue-500 flex flex-row-reverse">
              <button
                onClick={mode.onClick}
                key={mode.name}
                disabled={mode.disabled}
                data-tip={mode.dataTip}
                data-tip-skew="left"
                data-tip-cx="175"
                className={classes}
              >
                <FaClock />
              </button>
              {pushOut && <IsochroneControls key={1} />}
            </div>
          );
        }
        return (
          <div>
            <button
              // data-tip={mode.dataTip}
              key={mode.name}
              disabled={mode.disabled}
              data-tip={mode.dataTip}
              data-tip-skew="left"
              data-tip-cx="200"
              onClick={mode.onClick}
              className={classes}
            >
              {mode.icon}
            </button>
          </div>
        );
      })}
    </div>
  );
};
