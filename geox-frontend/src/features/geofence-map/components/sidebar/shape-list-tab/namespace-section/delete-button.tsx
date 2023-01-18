import { DeleteIcon } from "../../../../../../common/components/icons";
import { Namespace } from "../../../../../../client";
import { useShapes } from "../../../../hooks/use-shapes";
import { useContext } from "react";
import { UIContext } from "features/geofence-map/contexts/ui-context";

export const DeleteButton = ({ namespace }: { namespace: Namespace }) => {
  // delete a namespace
  const { confirmDelete, setHeading } = useContext(UIContext);

  const { removeNamespace } = useShapes();
  return (
    <button
      className="bg-slate-700 hover:bg-red-400 hover:border-red-400 disabled:bg-slate-700 disabled:cursor-not-allowed"
      disabled={namespace.name === "Default"}
      title="Delete this folder"
      data-tip={`Delete the ${namespace.name} folder`}
      data-tip-skew="right"
      onClick={(e) => {
        setHeading("Delete folder?");
        const coords = [e.clientX, e.clientY];
        confirmDelete(coords, () => {
          removeNamespace(namespace.id);
        });
      }}
    >
      <DeleteIcon className="fill-white" />
    </button>
  );
};
