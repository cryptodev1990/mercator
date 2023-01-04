// button to add a namespace

import { useGetNamespaces } from "features/geofence-map/hooks/use-openapi-hooks";
import toast from "react-hot-toast";
import { EditableLabel } from "../../../../../../common/components/editable-label";
import { useShapes } from "../../../../hooks/use-shapes";

export const AddButton = () => {
  const { addNamespace } = useShapes();
  const { data: namespaces } = useGetNamespaces();

  return (
    <div
      // center the div like a button and give it a slight border and make it beautfiul
      className="flex items-center justify-center hover:bg-gray-500 hover:border-gray-500 hover:text-white transition"
      data-tip="Add a shapes folder"
      data-tip-skew="right"
    >
      <EditableLabel
        className="font-bold text-md mx-1 select-none text-gray-400"
        value="+ Folder"
        // @ts-ignore
        onChange={(newName) => {
          const name = newName.trim();
          if (!name) {
            return toast.error("Namespace cannot be empty");
          }
          if (namespaces && namespaces.find((n) => n.name === name)) {
            return toast.error("Namespace already exists");
          }
          if (name === "+ Folder") {
            return toast.error("Please input valid namespace name");
          }

          addNamespace({
            name,
            properties: {},
          });
        }}
        disabled={false}
      />
    </div>
  );
};
