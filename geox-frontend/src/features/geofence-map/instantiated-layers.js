import { SelectionLayer as NebulaSelectionLayer } from "@nebula.gl/layers";
import { MVTLayer } from "@deck.gl/geo-layers";

const MAPBOX_TOKEN = process.env.REACT_APP_MAPBOX_TOKEN;

// https://codesandbox.io/s/selector-demo-7kspg?file=/src/App.js
const selectionLayer = new NebulaSelectionLayer({
  id: "selection",
  selectionType: "polygon",
  getPolygonOffset: ({ layerIndex }) => [0, -100],
  layerIds: ["scatter-plot-4"],
  getTentativeFillColor: () => [255, 0, 255, 100],
  getTentativeLineColor: () => [0, 0, 255, 255],
  getTentativeLineDashArray: () => [0, 0],
  lineWidthMinPixels: 1,
});

const mvtLayer = new MVTLayer({
  data: `https://a.tiles.mapbox.com/v4/mapbox.mapbox-streets-v7/{z}/{x}/{y}.vector.pbf?access_token=${MAPBOX_TOKEN}`,
  minZoom: 0,
  maxZoom: 23,
  getPolygonOffset: ({ layerIndex }) => [0, -90],
  getLineColor: [192, 192, 192],
  getFillColor: [140, 170, 180],
  getLineWidth: (f) => {
    if (f.properties.class === "street") {
      return 6;
    } else if (f.properties.class === "building") {
      return 10;
    } else {
      return 1;
    }
  },
  lineWidthMinPixels: 1,
});

//
export { selectionLayer, mvtLayer };
