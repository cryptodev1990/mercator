// button to add a namespace

import { useEffect } from "react";
import { toast } from "react-hot-toast";
import { EditableLabel } from "../../../../../../common/components/editable-label";
import { useShapes } from "../../../../hooks/use-shapes";

export const AddButton = () => {
  const { addNamespace, namespaces, namespacesError } = useShapes();

  useEffect(() => {
    if (namespacesError) {
      const error = (namespacesError as any)?.status;

      if (error === 409) {
        toast.error("Namespace already exists");
      } else if (error === 404) {
        toast.error("Namespace not found");
      } else {
        console.error(error);
        toast.error("Error adding namespace");
      }
    }
  }, [namespacesError]);

  return (
    <div
      // center the div like a button and give it a slight border and make it beautfiul
      className="flex items-center justify-center hover:bg-gray-500 hover:border-gray-500 hover:text-white transition"
      title="Add a namespace"
    >
      <EditableLabel
        className="font-bold text-md mx-1 select-none text-gray-400"
        value="+ Folder"
        // @ts-ignore
        onChange={(newName) => {
          const name = newName.trim();
          if (name !== "+ Folder" && !namespaces.find((n) => n.name === name)) {
            // clean up the name
            addNamespace({
              name,
              properties: {},
            });
          }
        }}
        disabled={false}
      />
    </div>
  );
};
