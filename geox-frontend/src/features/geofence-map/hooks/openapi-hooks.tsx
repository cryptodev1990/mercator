import { useMutation, useQuery, useQueryClient } from "react-query";
import {
  GeofencerService,
  GeoShape,
  GetAllShapesRequestType,
} from "../../../client";
import { useTokenInOpenApi } from "../../../hooks/use-token-in-openapi";

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

export const useGetAllShapesQuery = (queryType: GetAllShapesRequestType) => {
  const { isTokenSet } = useTokenInOpenApi();
  return useQuery<GeoShape[]>(
    ["geofencer"],
    () => {
      return GeofencerService.getAllShapesGeofencerShapesGet(queryType);
    },
    {
      refetchOnMount: false,
      enabled: isTokenSet,
      onSuccess(data) {
        console.log("saw data", data);
      },
    }
  );
};

export const useUpdateShapeMutation = () => {
  const queryClient = useQueryClient();
  return useMutation(GeofencerService.updateShapeGeofencerShapesUuidPut, {
    onSuccess(data: GeoShape) {
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
