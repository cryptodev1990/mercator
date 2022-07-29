import { EditorMode } from "./cursor-modes";

export interface GlobalEditorOptions {
  /** Block shapes from overlapping with each other */
  denyOverlap: boolean;
  cursorMode: EditorMode;
}
