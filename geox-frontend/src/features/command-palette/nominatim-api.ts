import axios from "axios";

const NOMINATIM_API_URL = "https://nominatim.openstreetmap.org/search";

export const getNominatimData = async (query: string) => {
  return axios.get(NOMINATIM_API_URL, {
    params: {
      q: query,
      format: "json",
      limit: 1,
      polygon_geojson: 1,
      addressdetails: 0,
      extratags: 0,
      namedetails: 0,
    },
  });
};
