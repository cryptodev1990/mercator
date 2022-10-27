import axios from "axios";
import { useCallback, useState } from "react";
import { toast } from "react-hot-toast";

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
  // eslint-disable-next-line  @typescript-eslint/no-unused-vars
  const [isochrones, _setIsochrones] = useState(null);

  // TODO this needs to be a backend URL
  const URL = "https://graphhopper.com/api/1/isochrone";
  const API_KEY = process.env.REACT_APP_GRAPHHOPPER_API_KEY;

  const getIsochrones = useCallback(
    async (point: Array<number>, timeInMinutes: number, profile: String) => {
      // TODO https://docs.graphhopper.com/#tag/Isochrone-API
      toast.loading("Loading isochrone...", { id: "isochrone" });
      setLoading(true);
      let res;
      try {
        res = await axios.get(URL, {
          params: {
            point: reverseArr(point).join(","),
            time_limit: timeInMinutes * 60,
            profile,
            key: API_KEY,
          },
        });
      } catch (err: any) {
        setError(err);
        toast.error("Error fetching isochrones");
      } finally {
        setLoading(false);
      }
      toast.success(
        "Isochrones loaded, " + timeInMinutes + " minutes and " + profile,
        {
          id: "isochrone",
        }
      );
      return res?.data.polygons[0];
    },
    [API_KEY]
  );

  return {
    getIsochrones,
    isochrones,
    error,
    loading,
  };
};
