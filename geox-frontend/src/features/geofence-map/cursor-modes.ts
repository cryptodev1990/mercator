export enum EditorMode {
  // Read existing
  ViewMode = "ViewMode",
  // select multiple shapes by drawing polygon
  MultiSelectMode = "MultiSelectMode",
  // Add a new polygon, corresponds to PolygonEditMode in nebula
  EditMode = "EditMode",
  // Modify an existing polygon, corresponds to ModifyMode in nebula
  ModifyMode = "ModifyMode",
  SplitMode = "SplitMode",
  // Select a group of polygons, using nebula selection layer
  LassoMode = "LassoMode",
  // Draws a polygon using a lasso
  LassoDrawMode = "LassoDrawMode",
  TranslateMode = "TranslateMode",
  DrawPolygonFromRouteMode = "DrawPolygonFromRoute",
  // IC DEMO
  DrawIsochroneMode = "DrawIsochroneMode",
}
