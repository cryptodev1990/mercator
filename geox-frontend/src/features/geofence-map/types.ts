import { GeoShapeCreate } from "client";
import { EditorMode } from "./cursor-modes";

export interface GlobalEditorOptions {
  /** Block shapes from overlapping with each other */
  denyOverlap: boolean;
  cursorMode: EditorMode;
}

export enum UIModalEnum {
  DeleteModal = "DeleteModal",
  ExportShapesModal = "ExportShapesModal",
  UploadShapesModal = "UploadShapesModal",
  DbSyncModal = "DbSyncModal",
  SupportModal = "SupportModal",
  BulkEditModal = "BulkEditModal",
}

export interface ShapesBulkUploadOptions {
  shapes: GeoShapeCreate[];
  onUploadProgress?: (progressEvent: ProgressEvent) => void;
}
