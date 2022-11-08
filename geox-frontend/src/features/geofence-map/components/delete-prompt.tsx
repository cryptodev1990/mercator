// DeletePrompt is a pop-up that asks the user to confirm that they want to delete a geofence

import { useContext } from "react";
import { UIContext } from "../contexts/ui-context";

export const DeletePrompt = () => {
  const { deletePromptCoords, onDeleteConfirm, onDeleteCancel } =
    useContext(UIContext);
  if (deletePromptCoords.length === 0) return null;
  return (
    <div
      className="
        absolute
        border
        shadow
        rounded-xl
        bg-white
        z-50
    "
      style={{
        top: deletePromptCoords[1] - 50,
        left: deletePromptCoords[0] + 50,
      }}
    >
      <div className="flex flex-col justify-center items-center p-2 ">
        {/* Add arrow-like point off to the left side of the div*/}
        <div
          className="
                absolute
                bg-white
                border border-gray-300
                border-solid
                shadow
                rounded
                z-50
            "
          style={{
            top: 50,
            left: -10,
            width: 0,
            height: 0,
            borderLeft: "10px solid transparent",
            borderRight: "10px solid transparent",
            borderTop: "10px solid white",
          }}
        />
        <div className="text-xl font-bold">Delete geofence?</div>
        <div className="text-sm text-gray-500">
          This action cannot be undone.
        </div>
        <div className="flex flex-row justify-center items-center">
          <button
            className="border border-gray-300 border-solid rounded p-2 m-2"
            onClick={() => {
              onDeleteConfirm();
            }}
          >
            Delete
          </button>
          <button
            className="border border-gray-300 border-solid rounded p-2 m-2"
            onClick={() => {
              onDeleteCancel();
            }}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};
