import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "react-query";
import { DrawPolygonMode, ViewMode } from "@nebula.gl/edit-modes";
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

export const useGetAllShapesQuery = (queryType: GetAllShapesRequestType) => {
  const { isTokenSet } = useTokenInOpenApi();
  return useQuery<GeoShape[]>(
    ["geofencer"],
    () => {
      return GeofencerService.getAllShapesGeofencerShapesGet(queryType);
    },
    {
      enabled: isTokenSet,
      onSuccess(data) {
        console.log("saw data", data);
      },
    }
  );
};

export const useEditMode = () => {
  const [editMode, setEditMode] = useState<any>(() => DrawPolygonMode);

  function escFunction(event: KeyboardEvent) {
    if (event.key === "Escape") {
      setEditMode(() => () => ViewMode);
    }
  }

  useEffect(() => {
    document.addEventListener("keydown", escFunction, false);

    return () => {
      document.removeEventListener("keydown", escFunction, false);
    };
  }, []);

  return { editMode, setEditMode };
};
