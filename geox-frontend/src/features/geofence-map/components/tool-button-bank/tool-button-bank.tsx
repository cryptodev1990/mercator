// @ts-ignore
import { useCursorMode } from "../../hooks/use-cursor-mode";

import { EditorMode } from "../../cursor-modes";
import {
  ScissorsIcon,
  LassoIcon,
  EditMarkupIcon,
  CursorLineIcon,
  ClockIcon,
  DrawPolygonIcon,
  DriveEtaIcon,
} from "../../../../common/components/icons";
import { useSelectedShapes } from "../../hooks/use-selected-shapes";
import { useEffect, useState } from "react";
import { IsochroneControls } from "./isochrone-controls";

interface ToolButtonBankMode {
  name: string;
  icon: JSX.Element;
  onClick: () => void;
  dataTip: string;
  active: boolean;
  disabled?: boolean;
  key: string;
}

export const ToolButtonBank = () => {
  const { cursorMode, setCursorMode } = useCursorMode();
  const { numSelected } = useSelectedShapes();
  const [pushOut, setPushOut] = useState(false);

  const modes: ToolButtonBankMode[] = [
    {
      name: "View",
      icon: <CursorLineIcon />,
      onClick: () => setCursorMode(EditorMode.ViewMode),
      dataTip: "View-only mode (Esc)",
      active: cursorMode === EditorMode.ViewMode,
      key: "mode-view",
    },
    {
      name: "Edit",
      icon: <DrawPolygonIcon />,
      onClick: () => setCursorMode(EditorMode.EditMode),
      dataTip: "Draw a shape by clicking",
      active: cursorMode === EditorMode.EditMode,
      key: "mode-edit",
    },
    {
      name: "Drive time",
      icon: <DriveEtaIcon />,
      onClick: () => setCursorMode(EditorMode.DrawIsochroneMode),
      dataTip: "Drive time distance",
      active: cursorMode === EditorMode.ModifyMode,
      key: "mode-drive-time",
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
      icon: <LassoIcon />,
      onClick: () => setCursorMode(EditorMode.LassoDrawMode),
      dataTip: "Freely draw a polygon",
      active: cursorMode === EditorMode.LassoDrawMode,
      key: "mode-polygon-lasso",
    },
    // {
    //   name: "Translate",
    //   icon: <BsArrowsMove />,
    //   onClick: () => setCursorMode(EditorMode.TranslateMode),
    //   dataTip: "Coming soon",
    //   disabled: true,
    //   active: cursorMode === EditorMode.TranslateMode,
    //   mode: "mode-translate"
    // },
    // {
    //   name: "Polygon from Route",
    //   icon: <MdOutlineDraw />,
    //   onClick: () => setCursorMode(EditorMode.DrawPolygonFromRouteMode),
    //   dataTip: "Coming soon",
    //   disabled: true,
    //   active: cursorMode === EditorMode.DrawPolygonFromRouteMode,
    //   mode: "mode-polygon-from-route"
    // },
    {
      name: "Alter",
      icon: <EditMarkupIcon />,
      onClick: () => setCursorMode(EditorMode.ModifyMode),
      dataTip: "Edit an existing shape",
      active: cursorMode === EditorMode.ModifyMode,
      disabled: numSelected !== 1,
      key: "mode-alter",
    },
    {
      name: "Split existing shape",
      icon: <ScissorsIcon />,
      onClick: () => setCursorMode(EditorMode.SplitMode),
      dataTip: "Split a selection by drawing through it",
      active: cursorMode === EditorMode.SplitMode,
      disabled: numSelected !== 1,
      key: "mode-split-existing-shape",
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
                <ClockIcon />
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
