import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { EditorMode } from "../cursor-modes";
import { useCursorMode } from "../hooks/use-cursor-mode";
import { useGetNamespaces } from "../hooks/use-openapi-hooks";
import { useSelectedShapes } from "../hooks/use-selected-shapes";
import { useShapes } from "../hooks/use-shapes";
import { useUiModals } from "../hooks/use-ui-modals";
import { UIModalEnum } from "../types";

export const RightClickMenu = () => {
  const [xPos, setXPos] = useState<string | null>(null);
  const [yPos, setYPos] = useState<string | null>(null);
  const [recentActivity, setRecentActivity] = useState<number>(0);
  const [options, setMenuOptions] = useState<string[]>([]);
  // read selection from context
  const {
    setShapeForPropertyEdit,
    clearSelectedFeatureIndexes,
    mapRef,
    deleteShapes,
  } = useShapes();
  const {
    selectedFeatureCollection,
    numSelected,
    isSelected,
    selectedUuids,
    clearSelectedShapeUuids,
  } = useSelectedShapes();

  function closeMenu() {
    setXPos(null);
    setYPos(null);
  }

  const { data: allNamespaces } = useGetNamespaces();

  const { openModal } = useUiModals();

  function cleanup() {
    setShapeForPropertyEdit(null);
    clearSelectedFeatureIndexes();
    clearSelectedShapeUuids();
    closeMenu();
    setCursorMode(EditorMode.ViewMode);
  }

  const {
    setCursorMode,
    options: editModeOptions,
    setOptions,
  } = useCursorMode();

  const listenerFunc = (event: MouseEvent) => {
    event.preventDefault();

    if (!selectedUuids.length) {
      setMenuOptions([
        "Draw",
        editModeOptions.denyOverlap ? "Enable overlap" : "Disable overlap",
      ]);
    }
    if (selectedUuids.length > 1) {
      setMenuOptions(["Bulk Delete", "Bulk Edit"]);
    }
    if (selectedUuids.length === 1) {
      setMenuOptions([
        "Edit Metadata",
        "Copy as GeoJSON",
        "Delete (Backspace)",
        "Unselect (Esc)",
      ]);
    }

    const xPos = event.pageX - 10 + "px";
    const yPos = event.pageY - 5 + "px";
    setXPos(xPos);
    setYPos(yPos);
  };

  useEffect(() => {
    // Make the context menu appear on right click only on the map
    if (mapRef?.current) {
      let ref = mapRef.current;
      ref.addEventListener("contextmenu", listenerFunc, false);

      return () => {
        ref.removeEventListener("contextmenu", listenerFunc, false);
      };
    }
  }, [mapRef, selectedUuids.length]);

  if (!xPos || !yPos) {
    return null;
  }

  function handleClickFor(fieldType: string) {
    switch (fieldType) {
      case "Draw":
        setCursorMode(EditorMode.EditMode);
        return;
      case "Edit Metadata":
        if (numSelected > 1) {
          toast.error("Please select only one shape to edit");
        }
        const selectedShape = allNamespaces
          ?.flatMap((x) => x.shapes ?? [])
          .find((shape) => isSelected(shape.uuid));
        if (!selectedShape) {
          toast.error("No shape detected");
          return;
        }
        setShapeForPropertyEdit(selectedShape);
        closeMenu();
        return;
      case "Copy as GeoJSON":
        if (selectedFeatureCollection) {
          navigator.clipboard.writeText(
            JSON.stringify(selectedFeatureCollection)
          );
          toast.success("Copied to clipboard");
        }
        closeMenu();
        return;
      case "Delete (Backspace)":
        deleteShapes(selectedUuids, {
          onSuccess: () => {
            cleanup();
          },
        });
        return;
      case "Unselect (Esc)":
        cleanup();
        return;
      case "Enable overlap":
      case "Disable overlap":
        // @ts-ignore
        setOptions((prevOptions) => {
          return { ...prevOptions, denyOverlap: !prevOptions.denyOverlap };
        });
        return;
      case "Bulk Edit":
        openModal(UIModalEnum.BulkEditModal);
        return;
      case "Bulk Delete":
        deleteShapes(selectedUuids, {
          onSuccess: () => {
            cleanup();
          },
        });
        return;
      default:
        return () => {
          setRecentActivity(recentActivity + 1);
        };
    }
  }

  return (
    <div
      style={{
        position: "fixed",
        top: yPos,
        left: xPos,
        zIndex: 9999,
        backgroundColor: "white",
        border: "1px solid black",
        boxShadow: "0px 0px 10px black",
        borderRadius: "5px",
      }}
      onMouseLeave={() => {
        setXPos(null);
        setYPos(null);
      }}
      onMouseMove={() => {
        setRecentActivity(Math.random());
      }}
    >
      <ul className="dropdown-content text-black menu p-1 rounded-box w-52 bg-white">
        {options.map((item) => (
          <li onClick={() => handleClickFor(item)} key={item}>
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};
