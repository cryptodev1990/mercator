import { useMutation, useQuery, useQueryClient } from "react-query";
import {
  GeofencerService,
  GeoShape,
  GetAllShapesRequestType,
} from "../../../client";
import { useTokenInOpenApi } from "../../../hooks/use-token-in-openapi";

export const useAddShapeMutation = () => {
  const queryClient = useQueryClient();
  const post = GeofencerService.createShapeGeofencerShapesPost;
  return useMutation(post, {
    onSuccess(data: GeoShape) {
      queryClient.fetchQuery("geofencer");
    },
    onError(error) {
      console.log("failed", error);
    },
    onSettled() {},
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
    }
  );
};

export const useUpdateShapeMutation = () => {
  const queryClient = useQueryClient();
  return useMutation(GeofencerService.updateShapeGeofencerShapesUuidPut, {
    onSuccess(data: GeoShape) {
      queryClient.fetchQuery("geofencer");
    },
    onError(error) {
      console.log("failed", error);
    },
  });
};

export const useBulkDeleteShapesMutation = () => {
  const queryClient = useQueryClient();
  return useMutation(
    GeofencerService.bulkSoftDeleteShapesGeofencerShapesDelete,
    {
      onSuccess(data: GeoShape) {
        queryClient.fetchQuery("geofencer");
      },
      onError(error) {
        console.log("failed", error);
      },
    }
  );
};
