import { CompositeLayer } from "@deck.gl/core";
import { BitmapLayer } from "@deck.gl/layers";
import { EditableGeoJsonLayer } from "@nebula.gl/layers";
import { TransformMode } from "@nebula.gl/edit-modes";

export class GeoJsonImageLayer extends CompositeLayer<any> {
  // Force update layer and re-render sub layers when viewport changes
  renderLayers() {
    // @ts-ignore
    const { bounds, image, onEdit } = this.props;
    return [
      // @ts-ignore
      new EditableGeoJsonLayer({
        id: "bitmap-layer-editable",
        // @ts-ignore
        mode: TransformMode,
        pickable: true,
        selectedFeatureIndexes: [0],
        onEdit,
        data: {
          // @ts-ignore
          type: "FeatureCollection",
          features: [
            {
              type: "Feature",
              geometry: {
                type: "Polygon",
                coordinates: [
                  [bounds[0], bounds[1], bounds[2], bounds[3], bounds[0]],
                ],
              },
            },
          ],
        },
      }),
      // @ts-ignore
      new BitmapLayer({
        id: "bitmap-layer",
        opacity: 0.3,
        pickable: true,
        bounds,
        image,
      }),
    ];
  }
}
