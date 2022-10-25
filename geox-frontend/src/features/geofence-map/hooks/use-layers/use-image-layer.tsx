import { useEffect, useState } from "react";
import { WebMercatorViewport } from "@deck.gl/core";
import { GeoJsonImageLayer } from "../../../../common/geojson-image-layer";
import { useViewport } from "../use-viewport";

type Bounds = [number[], number[], number[], number[]];

export const useImageLayer = () => {
  const { viewport } = useViewport();
  const [bounds, setBounds] = useState<Bounds | null>(null);

  useEffect(() => {
    if (bounds) {
      return;
    }
    if (!viewport || !viewport.width || !viewport.height) {
      return;
    }
    const wmv = new WebMercatorViewport(viewport);
    const nw = wmv.unproject([0, 0]);
    const se = wmv.unproject([viewport.width * 0.5, viewport.height * 0.5]);

    setBounds([
      [se[0], se[1]],
      [nw[0], se[1]],
      [nw[0], nw[1]],
      [se[0], nw[1]],
    ]);
    // setBounds();
  }, [viewport, bounds]);

  // image layer
  return new GeoJsonImageLayer({
    id: "image-layer",
    // @ts-ignore
    bounds,
    onEdit: (e: any) => {
      const { updatedData } = e;
      const [a, b, c, d] = updatedData.features[0].geometry.coordinates[0];
      setBounds([a, b, c, d]);
    },
    image:
      "https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/sf-districts.png",
  });
};
