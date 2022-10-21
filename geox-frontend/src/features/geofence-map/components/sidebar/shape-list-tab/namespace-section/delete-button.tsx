import { MdDelete } from "react-icons/md";
import { Namespace } from "../../../../../../client";
import { useShapes } from "../../../../hooks/use-shapes";

export const DeleteButton = ({ namespace }: { namespace: Namespace }) => {
  // delete a namespace
  const { removeNamespace } = useShapes();
  return (
    <button
      className="bg-slate-700 hover:bg-red-400 hover:border-red-400 disabled:bg-slate-700 disabled:cursor-not-allowed"
      disabled={namespace.name === "Default"}
      title="Delete this namespace"
      data-tip={`Delete the ${namespace.name} folder`}
      data-tip-skew="right"
      onClick={() => {
        removeNamespace(namespace.id);
      }}
    >
      <MdDelete className="fill-white" />
    </button>
  );
};
