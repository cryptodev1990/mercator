export const MODES = {
  // Read existing
  ViewMode: "ViewMode",
  // Add a new polygon, corresponds to PolygonEditMode in nebula
  EditMode: "EditMode",
  // Modify an existing polygon, corresponds to ModifyMode in nebula
  ModifyMode: "ModifyMode",
  // Select a group of polygons.
  // This is PolygonEditMode + a new layer in Nebula, combined with deck.
  // The area at the intersection of the lasso and the existing features is selected.
  LassoMode: "LassoMode",
  TranslateMode: "TranslateMode",
};
