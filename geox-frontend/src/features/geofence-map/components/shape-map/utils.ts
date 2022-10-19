import { InteractiveState } from "@deck.gl/core/lib/deck";
import { EditorMode } from "../../cursor-modes";

export function getCursorFromCursorMode(
  e: InteractiveState,
  cursorMode: EditorMode
): string {
  switch (cursorMode) {
    case EditorMode.ViewMode:
      if (e.isDragging) {
        return "grabbing";
      }
      if (e.isHovering) {
        return "pointer";
      }
      return "grab";
    case EditorMode.EditMode:
    case EditorMode.LassoDrawMode:
      return "crosshair";
    case EditorMode.SplitMode:
      return 'url("/scissors.png"), cell';
    case EditorMode.ModifyMode:
      if (e.isDragging) {
        return "grabbing";
      }
      if (e.isHovering) {
        return "pointer";
      }
      return "grab";
    case EditorMode.DrawIsochroneMode:
      return "crosshair";
    default:
      return "pointer";
  }
}
