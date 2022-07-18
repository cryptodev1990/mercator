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
  } catch (error) {
    console.log(error);
  }
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
          "?&geometries=geojson&ignore=access,oneways,restrictions&access_token=" +
          process.env.REACT_APP_MAPBOX_TOKEN
      )
      .then((res) => {
        console.log(res);
        if (res.data.code === "NoMatch") {
          throw new Error("no match");
        }
        const topMatch = res.data.matchings[0];
        return topMatch.geometry;
      });
  } catch (error) {
    console.log(error);
  }
}
