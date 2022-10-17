import { useMutation } from "react-query";
import { NamespacesService } from "../../../../client";

export const useAddNamespaceMutation = () => {
  return useMutation(NamespacesService.postNamespacesGeofencerNamespacesPost);
};

export const useDeleteNamespaceMutation = () => {
  return useMutation(
    NamespacesService.deleteNamespacesGeofencerNamespacesNamespaceIdDelete
  );
};
