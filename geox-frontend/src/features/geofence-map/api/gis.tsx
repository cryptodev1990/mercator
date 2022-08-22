import axios from "axios";

export async function getRoute(points: number[][]) {
  if (!points[0][0]) {
    return;
  }
  try {
    return axios.get(
      "https://graphhopper.com/api/1/route?" +
        points.map((d) => `point=${d[1]},${d[0]}`).join("&") +
        `&profile=car&locale=de&calc_points=true&key=${process.env.REACT_APP_GRAPHHOPPER_API_KEY}`
    );
  } catch (error) {}
}

export async function mapMatch(datum: any) {
  if (!datum) {
    return;
  }
  const points = datum?.geometry?.coordinates;

  try {
    return axios
      .get(
        "https://api.mapbox.com/matching/v5/mapbox/driving/" +
          points.map((d: any) => `${d[0]},${d[1]}`).join(";") +
          "?&" +
          "radiuses=" +
          points.map((d: any) => `50`).join(";") +
          "&geometries=geojson&steps=true&tidy=true&ignore=restrictions&access_token=" +
          process.env.REACT_APP_MAPBOX_TOKEN
      )
      .then((res) => {
        if (res.data.code === "NoMatch") {
          throw new Error("no match");
        }
        // const lineStringTracepoints = res.data.tracepoints.map(
        //   (x: any, i: number) => {
        //     console.log(x);
        //     if (x === null) {
        //       return points[i];
        //     }
        //     return x.location;
        //   }
        // );
        const coordinates = res.data.matchings
          .map((x: any) => x.geometry.coordinates)
          .flat();
        return {
          type: "Feature",
          geometry: {
            type: "LineString",
            coordinates,
          },
          properties: {},
        };
      });
  } catch (error) {
    console.log(error);
  }
}
