import { useContext } from "react";
import { useMutation, useQuery, useQueryClient } from "react-query";
import simplur from "simplur";
import {
  CeleryTaskResponse,
  CeleryTaskResult,
  GeofencerService,
  GeoShape,
  TasksService,
  ShapeCountResponse,
  GeoShapeCreate,
  GetAllShapesRequestType,
} from "../../../client";
import { useTokenInOpenApi } from "../../../hooks/use-token-in-openapi";
import toast from "react-hot-toast";
import { useState } from "react";
import { GeoShapeMetadata } from "../../../client/models/GeoShapeMetadata";
import { DeckContext } from "../contexts/deck-context";
import { useCursorMode } from "./use-cursor-mode";
import { difference } from "@turf/turf";

export const useAddShapeMutation = () => {
  const queryClient = useQueryClient();
  const { options } = useCursorMode();
  const post = GeofencerService.createShapeGeofencerShapesPost;
  const { triggerTileRefresh, deckRef } = useContext(DeckContext);

  return useMutation(post, {
    onMutate: async (newData: GeoShapeCreate) => {
      const shouldRemoveOverlap =
        options?.denyOverlap &&
        typeof deckRef.current !== "undefined" &&
        deckRef.current.deck &&
        deckRef.current.deck.layerManager;

      // feature remove overlap
      if (shouldRemoveOverlap) {
        const layerManager = deckRef.current.deck.layerManager;
        const mvtLayer = layerManager
          .getLayers()
          .find((x: any) => x.id === "geofence-mvt");
        // TODO this produces way more features than it needs to, what gives?
        const currentFeatures = mvtLayer.getRenderedFeatures();
        for (const feat of currentFeatures) {
          const diffShape = difference(newData.geojson as any, feat);
          if (diffShape === null) {
            return;
          }
          newData.geojson = diffShape as any;
        }
      }
    },
    onSuccess(data: GeoShape) {
      queryClient.fetchQuery("geofencer");
      triggerTileRefresh();
    },
    onError(error: any) {
      toast.error(`Shape failed to add`);
      console.error(error);
    },
  });
};

export const useGetAllShapesMetadata = () => {
  const { isTokenSet } = useTokenInOpenApi();
  return useQuery<GeoShapeMetadata[]>(
    ["geofencer"],
    () => {
      return GeofencerService.getAllShapeMetadataGeofencerShapeMetadataGet(
        10000, // limit
        0 // offset
      );
    },
    {
      refetchOnMount: false,
      enabled: isTokenSet,
      onError(error: any) {
        toast.remove();
        toast.error(`Shapes failed to fetch (${error})`);
      },
    }
  );
};

export const useGetOneShapeByUuid = (uuid: string) => {
  return useQuery<GeoShape | null>(
    ["shape", uuid],
    ({ meta }) => {
      if (!uuid) {
        return Promise.resolve(null);
      }
      return GeofencerService.getShapeGeofencerShapesUuidGet(uuid);
    },
    {
      staleTime: 0,
      cacheTime: 0,
      onError(error: any) {
        toast.error(`Shapes failed to fetch (${error.detail ?? error})`);
      },
    }
  );
};

export const useUpdateShapeMutation = () => {
  const queryClient = useQueryClient();
  const { triggerTileRefresh } = useContext(DeckContext);
  return useMutation(GeofencerService.updateShapeGeofencerShapesUuidPut, {
    onSuccess(data: GeoShape) {
      queryClient.fetchQuery("geofencer");
      // Optimistically update to the new value
      triggerTileRefresh();
    },
    onError(error: any) {
      toast.error(`Shapes failed to update (${error.detail ?? error})`);
    },
  });
};

export const useBulkDeleteShapesMutation = () => {
  const queryClient = useQueryClient();
  const { triggerTileRefresh } = useContext(DeckContext);
  return useMutation(
    GeofencerService.bulkDeleteShapesGeofencerShapesBulkDelete,
    {
      onSuccess(data: ShapeCountResponse) {
        toast.success(simplur`Deleted ${data.num_shapes} shape[|s]`);
        queryClient.fetchQuery("geofencer");
        triggerTileRefresh();
      },
      onError(error) {
        toast.error(`Shapes failed to delete (${error})`);
      },
    }
  );
};

export const useBulkAddShapesMutation = () => {
  const queryClient = useQueryClient();
  const { triggerTileRefresh } = useContext(DeckContext);

  return useMutation(GeofencerService.bulkCreateShapesGeofencerShapesBulkPost, {
    onSuccess(data: ShapeCountResponse) {
      queryClient.fetchQuery("geofencer");
      triggerTileRefresh();
    },
    onError(error: any) {
      toast.error(`Shapes failed to add (${error?.detail})`);
    },
  });
};

export const useNumShapesQuery = () => {
  return useQuery<ShapeCountResponse>(
    ["numShapes"],
    () => {
      return GeofencerService.getShapeCountGeofencerShapesOpCountGet();
    },
    {
      refetchOnWindowFocus: true,
      refetchOnMount: true,
      onError(error) {
        toast.error(`Shapes failed to fetch (${error})`);
      },
    }
  );
};

export const useGetAllShapes = (limit: number, offset: number) => {
  return useQuery<GeoShape[] | null>(
    ["allshapes"],
    () => {
      return GeofencerService.getAllShapesGeofencerShapesGet(
        GetAllShapesRequestType.ORGANIZATION,
        offset,
        limit
      );
    },
    {
      retry: false,
      cacheTime: 0,
      staleTime: 0,
      onError(error: any) {
        toast.error(`Shapes failed to fetch (${error.detail ?? error})`);
      },
    }
  );
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
    GeofencerService.shapesExportShapesExportPost,
    {
      onSuccess(data: CeleryTaskResponse) {
        queryClient.fetchQuery(["copyTask", data.task_id]);
      },
      onError(error: any, variables: any, context: any) {
        if (error.status === 403) {
          toast.error(
            "Copy task failed. Contact support@mercator.tech to enable this feature"
          );
        } else {
          toast.error(`Copy task failed (${error.detail ?? error})`);
        }
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
