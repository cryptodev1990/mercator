import axios from "axios";
import { useState } from "react";

export const useIsochrones = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isochrones, setIsochrones] = useState(null);

  const URL = "https://graphhopper.com/api/1/isochrone";
  // const API_KEY = process.env.REACT_APP_GRAPHHOPPER_API_KEY;

  console.error("not implemented");
  async function getIsochrones(
    point: Array<number>,
    timeInMinutes: number,
    profile: String
  ) {
    // TODO https://docs.graphhopper.com/#tag/Isochrone-API
    const res = await axios.get(URL, {
      params: {
        point: point.join(","),
        time_limit: timeInMinutes * 60,
        profile,
        api_key: null,
      },
    });
    return res.data;
  }

  return {
    getIsochrones,
    isochrones,
    error,
    loading,
  };
};
