import { useContext } from "react";
import { GeofencerContext } from "./context";
import { Feature, GeoShapeCreate } from "../../client";
import buffer from "@turf/buffer";
import centroid from "@turf/centroid";

import { useAddShapeMutation } from "./hooks/openapi-hooks";
import { CommandPalette } from "../command-palette/component";
import { useIsochrones } from "../../hooks/use-isochrones";

export const GeofencerCommandPalette = () => {
  const { tentativeShapes, setTentativeShapes, setViewport } =
    useContext(GeofencerContext);
  const { mutate: addShape } = useAddShapeMutation();
  const { getIsochrones, error: isochroneError } = useIsochrones();

  return (
    <CommandPalette
      onNominatim={(res: any) => {
        setViewport(res);
      }}
      // Commit data to the server
      onPublish={() => {
        const newShapes: GeoShapeCreate[] = [];
        for (const ns of tentativeShapes) {
          // TODO add shapes in bulk here
          addShape({
            name: ns?.geojson.properties.name || "New shape",
            geojson: ns.geojson,
          } as GeoShapeCreate);
          newShapes.push(ns);
        }
      }}
      onOSM={(res: Feature[]) => {
        const geoshapes = res.map((f: Feature) => {
          return {
            name: f.properties.name,
            geojson: f,
            tentative: true,
          } as GeoShapeCreate;
        });
        setTentativeShapes([...geoshapes]);
      }}
      onBuffer={(bufferSize: number, bufferUnits: string) => {
        const newShapes: GeoShapeCreate[] = [];
        for (const s of tentativeShapes) {
          const bufferedGeom = buffer(
            centroid(s.geojson as any, { properties: s.geojson.properties }),
            bufferSize,
            {
              units: bufferUnits as any,
            }
          );

          newShapes.push({
            name: s.name,
            geojson: bufferedGeom as any,
          });
        }

        setTentativeShapes(newShapes);
      }}
      onIsochrone={async (num: number, timeUnits: string) => {
        const timeInSeconds = num * 60;
        const newShapes: GeoShapeCreate[] = [];
        for (const s of tentativeShapes) {
          const pt = s.geojson as any;
          const chrone = await getIsochrones(
            centroid(pt) as any,
            timeInSeconds,
            "car"
          );
          newShapes.push({
            ...s,
            geojson: chrone as any,
          });
        }
        setTentativeShapes(newShapes);
      }}
    />
  );
};
