import { useMutation, useQuery, useQueryClient } from "react-query";
import {
  CeleryTaskResponse,
  CeleryTaskResult,
  GeofencerService,
  GeoShape,
  GetAllShapesRequestType,
  TasksService,
  ShapeCountResponse,
  GeoShapeUpdate,
} from "../../../client";
import { useTokenInOpenApi } from "../../../hooks/use-token-in-openapi";
import toast from "react-hot-toast";
import { useState } from "react";

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

export const useUpdateShapeMutation = (optimistic = true) => {
  const queryClient = useQueryClient();
  return useMutation(GeofencerService.updateShapeGeofencerShapesUuidPut, {
    onMutate: async (newShape: GeoShapeUpdate) => {
      if (!optimistic) {
        return;
      }
      // Cancel any outgoing refetches (so they don't overwrite our optimistic update)
      await queryClient.cancelQueries(["geofencer"]);
      // Snapshot the previous value
      const previousValue = queryClient.getQueryData(["geofencer"]);
      const optimisticNewShape = {
        uuid: newShape.uuid,
        geojson: newShape.geojson,
        name: newShape.name,
      } as GeoShape;
      // Optimistically update to the new value
      queryClient.setQueryData(["geofencer"], (old: GeoShape[] | undefined) => {
        if (!old) {
          return [optimisticNewShape];
        }
        return old.map((shape) => {
          if (shape.uuid === newShape.uuid) {
            return optimisticNewShape;
          }
          return shape;
        });
      });
      return { previousValue };
    },
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
    GeofencerService.bulkDeleteShapesGeofencerShapesBulkDelete,
    {
      onSuccess(data: ShapeCountResponse) {
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
    onSuccess(data: ShapeCountResponse) {
      queryClient.fetchQuery("geofencer");
    },
    onError(error) {
      toast.error(`Shapes failed to add (${error})`);
    },
  });
};

export const usePollCopyTaskQuery = (taskId: string | undefined) => {
  const queryClient = useQueryClient();
  return useQuery<CeleryTaskResult>(
    ["copyTask", taskId],
    () => {
      if (taskId) {
        return TasksService.getStatusTasksResultsTaskIdGet(taskId);
      }
      return Promise.resolve({} as CeleryTaskResult);
    },
    {
      refetchInterval: (data) =>
        data?.task_status === "SUCCESS" ? false : 2000,
      refetchOnWindowFocus: false,
      enabled: taskId !== undefined,
      refetchOnMount: false,
      onError(error) {
        toast.error(`Copy task failed (${error})`);
      },
      onSuccess(data: CeleryTaskResult) {
        if (data?.task_status === "SUCCESS") {
          toast.success(
            `Shapes copied successfully (${data.task_result.num_rows} shapes)`
          );
        }
        // cancel polling
        queryClient.cancelQueries(["copyTask", taskId]);
      },
    }
  );
};

export const useTriggerCopyTaskMutation = () => {
  const queryClient = useQueryClient();
  return useMutation<CeleryTaskResponse>(
    TasksService.runCopyTaskTasksCopyShapesPost,
    {
      onSuccess(data: CeleryTaskResponse) {
        queryClient.fetchQuery(["copyTask", data.task_id]);
      },
      onError(error) {
        toast.error(`Copy task failed (${error})`);
      },
    }
  );
};

export const useDebouncedMutation = (mutationFn: any, options: any) => {
  const mutation = useMutation(mutationFn, options);
  const [isDebouncing, setIsDebouncing] = useState(false);
  let timer: any;

  // @ts-ignore
  const debouncedMutate = (variables: any, { debounceMs, ...options }) => {
    clearTimeout(timer);
    setIsDebouncing(true);
    timer = setTimeout(() => {
      mutation.mutate(variables, options);
      setIsDebouncing(false);
    }, debounceMs);
  };

  return { isDebouncing, debouncedMutate, ...mutation };
};

export const useDebouncedUpdateShape = () => {
  const { isDebouncing, debouncedMutate, isLoading, isSuccess } =
    useDebouncedMutation(GeofencerService.updateShapeGeofencerShapesUuidPut, {
      onError(error: any) {
        toast.error(`Shapes failed to update (${error})`);
      },
    });

  return { isDebouncing, debouncedMutate, isLoading, isSuccess };
};
