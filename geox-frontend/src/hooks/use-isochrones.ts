import axios from "axios";
import { useCallback, useState } from "react";

function reverseArr(input: any) {
  var ret = [];
  for (var i = input.length - 1; i >= 0; i--) {
    ret.push(input[i]);
  }
  return ret;
}

export const useIsochrones = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isochrones, setIsochrones] = useState(null);

  const URL = "https://graphhopper.com/api/1/isochrone";
  const API_KEY = process.env.REACT_APP_GRAPHHOPPER_API_KEY;

  const getIsochrones = useCallback(
    async (point: Array<number>, timeInMinutes: number, profile: String) => {
      // TODO https://docs.graphhopper.com/#tag/Isochrone-API
      const res = await axios.get(URL, {
        params: {
          point: reverseArr(point).join(","),
          time_limit: timeInMinutes,
          profile,
          key: API_KEY,
        },
      });
      return res.data;
    },
    []
  );

  return {
    getIsochrones,
    isochrones,
    error,
    loading,
  };
};
