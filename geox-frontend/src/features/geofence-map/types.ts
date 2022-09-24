import { EditorMode } from "./cursor-modes";

export interface GlobalEditorOptions {
  /** Block shapes from overlapping with each other */
  denyOverlap: boolean;
  cursorMode: EditorMode;
}

export enum UIModalEnum {
  DeleteModal = "DeleteModal",
  UploadShapesModal = "UploadShapesModal",
  DbSyncModal = "DbSyncModal",
  SupportModal = "SupportModal",
}
