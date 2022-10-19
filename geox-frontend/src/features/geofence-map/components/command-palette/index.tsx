import { useContext, useEffect } from "react";
import { GeofencerContext } from "../../contexts/geofencer-context";
import { Feature, GeoShapeCreate } from "../../../../client";
import buffer from "@turf/buffer";
import centroid from "@turf/centroid";

import { Menu } from "./menu";
import { useIsochrones } from "../../../../hooks/use-isochrones";
import { useShapes } from "../../hooks/use-shapes";
import { toast } from "react-hot-toast";
import { polygon, union } from "@turf/turf";

export const CommandPalette = () => {
  const { tentativeShapes, setTentativeShapes, setViewport } =
    useContext(GeofencerContext);
  const {
    shapeMetadata,
    deleteShapes: bulkDeleteShapes,
    addShape,
  } = useShapes();
  const { getIsochrones, error: isochroneError } = useIsochrones();

  useEffect(() => {
    if (isochroneError) {
      toast.error(isochroneError);
    }
  }, [isochroneError]);

  return (
    <Menu
      onNominatim={(res: any) => {
        setViewport(res);
      }}
      onDelete={() => {
        bulkDeleteShapes(shapeMetadata.map((s: any) => s.uuid));
        setTentativeShapes([]);
      }}
      onUnion={() => {
        // get a union of a list of shapes using turf
        // https://turfjs.org/docs/#union
        // get a union of a list of
        let newShape = polygon([]);
        for (const shape of tentativeShapes) {
          newShape = union(shape.geojson as any, newShape) as any;
        }
        addShape({
          name: "New shape",
          geojson: newShape as any,
        });
        setTentativeShapes([]);
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
      onIsochrone={async (num: number, timeUnits: string, mode: string) => {
        const timeInSeconds = num * 60;
        const newShapes: GeoShapeCreate[] = [];
        let i = 0;
        for (const s of tentativeShapes) {
          if (i >= 10) {
            break;
          }

          const pt = s.geojson as any;
          i += 1;

          try {
            const chrone = await getIsochrones(
              centroid(pt).geometry.coordinates,
              timeInSeconds,
              mode
            );

            newShapes.push({
              ...s,
              geojson: chrone.polygons[0] as any,
            });
          } catch (err) {
            console.error(err);
            continue;
          }
        }
        setTentativeShapes(newShapes);
      }}
    />
  );
};
