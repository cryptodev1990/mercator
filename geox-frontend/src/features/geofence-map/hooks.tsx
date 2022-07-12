import { useMutation, useQuery, useQueryClient } from "react-query";
import {
  GeofencerService,
  GeoShape,
  GetAllShapesRequestType,
} from "../../client";
import { useTokenInOpenApi } from "../../hooks/use-token-in-openapi";

export const useAddShapeMutation = () => {
  const queryClient = useQueryClient();
  return useMutation(GeofencerService.createShapeGeofencerShapesPost, {
    onSuccess(data: GeoShape[]) {
      console.log("onSuccess createShapeMutation");
      queryClient.fetchQuery("geofencer");
    },
    onError(error) {
      console.log("failed", error);
    },
    onSettled() {
      console.log("done");
    },
  });
};

export const useGetAllShapesQuery = () => {
  const { isTokenSet } = useTokenInOpenApi();
  return useQuery<GeoShape[]>(
    ["geofencer"],
    () => {
      return GeofencerService.getAllShapesGeofencerShapesGet(
        GetAllShapesRequestType.USER
      );
    },
    {
      enabled: isTokenSet,
      onSuccess(data) {
        console.log("saw data", data);
      },
    }
  );
};
