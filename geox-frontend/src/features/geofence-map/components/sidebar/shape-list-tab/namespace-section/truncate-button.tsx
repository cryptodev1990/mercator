import { DeleteIcon } from "../../../../../../common/components/icons";
import { Namespace, NamespacesService } from "../../../../../../client";
import { useShapes } from "../../../../hooks/use-shapes";
import { useContext } from "react";
import { UIContext } from "features/geofence-map/contexts/ui-context";
import { useMutation, useQueryClient } from "react-query";
import toast from "react-hot-toast";

export const TruncateButton = ({ namespace }: { namespace: Namespace }) => {
  // delete a namespace
  const { confirmDelete, setHeading } = useContext(UIContext);
  const { setTileUpdateCount, tileUpdateCount } = useShapes();
  const qc = useQueryClient();

  const truncateMutation = useMutation(NamespacesService.patchNamespaceShapes, {
    onSuccess: async (newNamespace) => {
      await qc.cancelQueries(["geofencer"]);
      const previousNamespaces: Namespace[] | undefined = qc.getQueryData([
        "geofencer",
      ]);
      if (previousNamespaces) {
        qc.setQueryData(
          ["geofencer"],
          previousNamespaces.map((prevNamespace: Namespace) =>
            prevNamespace.id === newNamespace.id ? newNamespace : prevNamespace
          )
        );
        setTileUpdateCount(tileUpdateCount + 1);
      }
    },
    onError: (error: any) => {
      if (error.message) toast.error(error.message);
      else toast.error("Error occured truncating namespace");
    },
  });

  return (
    <button
      className="bg-slate-700 hover:bg-red-400 hover:border-red-400 disabled:bg-slate-700 disabled:cursor-not-allowed"
      title="Delete this folder"
      data-tip={`Delete the ${namespace.name} folder`}
      data-tip-skew="right"
      onClick={(e) => {
        setHeading("Delete folder?");
        const coords = [e.clientX, e.clientY];
        confirmDelete(coords, () => {
          truncateMutation.mutate({
            namespace_id: namespace.id,
            requestBody: { data: [] },
          });
        });
      }}
    >
      <DeleteIcon className="fill-white" />
    </button>
  );
};
