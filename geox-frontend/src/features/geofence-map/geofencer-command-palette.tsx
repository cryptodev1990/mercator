import { useContext } from "react";
import { GeofencerContext } from "./context";
import { Feature, GeoShapeCreate } from "../../client";
import buffer from "@turf/buffer";

import { useAddShapeMutation } from "./hooks/openapi-hooks";
import { CommandPalette } from "../command-palette/component";

export const GeofencerCommandPalette = () => {
  const { tentativeShapes, setTentativeShapes, setViewport } =
    useContext(GeofencerContext);
  const { mutate: addShape } = useAddShapeMutation();

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
          const bufferedGeom = buffer(s.geojson as any, bufferSize, {
            units: bufferUnits as any,
          });

          newShapes.push({
            ...s,
            geojson: bufferedGeom as any,
          });
        }

        setTentativeShapes(newShapes);
      }}
    />
  );
};
