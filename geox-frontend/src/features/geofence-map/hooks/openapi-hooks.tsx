import { useMutation, useQuery, useQueryClient } from "react-query";
import {
  GeofencerService,
  GeoShape,
  GetAllShapesRequestType,
} from "../../../client";
import { useTokenInOpenApi } from "../../../hooks/use-token-in-openapi";
import toast from "react-hot-toast";

export const useAddShapeMutation = () => {
  const queryClient = useQueryClient();
  const post = GeofencerService.createShapeGeofencerShapesPost;

  return useMutation(post, {
    onSuccess(data: GeoShape) {
      queryClient.fetchQuery("geofencer");
    },
    onError(error: any) {
      toast.error(`Shape failed to add`);
      console.error(error);
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
      onError(error: any) {
        toast.error(`Shapes failed to fetch (${error})`);
      },
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
      toast.error(`Shapes failed to update (${error})`);
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
        toast.error(`Shapes failed to delete (${error})`);
      },
    }
  );
};

export const useBulkAddShapesMutation = () => {
  const queryClient = useQueryClient();
  return useMutation(GeofencerService.bulkCreateShapesGeofencerShapesBulkPost, {
    onSuccess(data: GeoShape) {
      queryClient.fetchQuery("geofencer");
    },
    onError(error) {
      toast.error(`Shapes failed to add (${error})`);
    },
  });
};
