import clsx from "clsx";
import { useEffect, useState } from "react";
import { BiCaretDown, BiSave } from "react-icons/bi";
import { Namespace } from "../../../../../../client";
import { CancelIcon } from "../../../../../../common/components/icons";
import { useSelectedShapes } from "../../../../hooks/use-selected-shapes";
import { useShapes } from "../../../../hooks/use-shapes";
import { useViewport } from "../../../../hooks/use-viewport";
import simplur from "simplur";
import Loading from "react-loading";

const CancelButton = () => {
  const { setTentativeShapes } = useShapes();
  return (
    <button
      className="btn btn-xs text-white rounded hover:text-red-400"
      onClick={() => setTentativeShapes([])}
    >
      <CancelIcon />
    </button>
  );
};

const SaveButton = ({
  selectedFolder,
}: {
  selectedFolder: Namespace | null;
}) => {
  const {
    tentativeShapes,
    setTentativeShapes,
    namespaces,
    bulkAddShapes,
    setVisibleNamespaces,
  } = useShapes();
  useShapes();
  const { snapToBounds } = useViewport();
  const { clearSelectedShapeUuids } = useSelectedShapes();
  const [locked, setLocked] = useState(false);

  return (
    <div className="flex flex-row flex-grow">
      <button
        className="
          btn
          w-full
          bg-green-600
          text-white
        "
        disabled={locked}
        onClick={() => {
          setLocked(true);
          bulkAddShapes(
            tentativeShapes.map((shape) => ({
              ...shape,
              namespace: selectedFolder?.id,
            })),
            {
              onSuccess: () => {
                snapToBounds({ category: "tentative" });
                setTentativeShapes([]);
                setVisibleNamespaces([selectedFolder]);
                clearSelectedShapeUuids();
                setLocked(false);
              },
              onError: (e) => {
                console.error(e);
              },
            }
          );
        }}
      >
        {!locked && (
          <>
            <BiSave></BiSave> Save
          </>
        )}
        {locked && <Loading className="spin" height={20} width={20} />}
      </button>
    </div>
  );
};

// dropdown of the current namespaces
const NamespaceSection = ({ selectedFolder, setSelectedFolder }: any) => {
  const { namespaces } = useShapes();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const handleDropdownClick = () => {
    setIsDropdownOpen(!isDropdownOpen);
  };

  const handleNamespaceClick = (namespace: Namespace) => {
    setSelectedFolder(namespace);
    setIsDropdownOpen(false);
  };

  return (
    <div className="flex flex-row items-center">
      <div className="flex flex-row items-center">
        <p className="text-white text-sm mr-2">Upload to folder:</p>
        <div className="flex flex-row items-center">
          <div
            className="flex flex-row items-center justify-center bg-white rounded w-full h-8 m-2 p-2"
            onClick={handleDropdownClick}
          >
            <BiCaretDown className="fill-black" />
            <p
              className={clsx({
                ["text-black text-sm"]: true,
                ["opacity-50"]: selectedFolder,
              })}
            >
              {selectedFolder?.name || "Select a folder"}{" "}
            </p>
          </div>
          {isDropdownOpen && (
            <div className="absolute z-10 bg-white rounded-md shadow-md">
              <div className="text-black">
                <CancelIcon
                  className="float-right m-1 hover:cursor-pointer"
                  onClick={() => setIsDropdownOpen(false)}
                />
              </div>
              {namespaces.map((namespace) => (
                <div
                  className="flex flex-row items-center justify-start w-full h-8 rounded-md cursor-pointer hover:bg-gray-200 p-2"
                  onClick={() => handleNamespaceClick(namespace)}
                >
                  <p className="text-black text-sm">{namespace.name}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export const TentativeButtonBank = () => {
  // Button bank that pops up for uploaded shapes or shapes from the command palette
  const { tentativeShapes, setActiveNamespace, namespaces } = useShapes();
  const { snapToBounds } = useViewport();
  const [selectedFolder, setSelectedFolder] = useState<Namespace | null>(null);

  useEffect(() => {
    setActiveNamespace(null);
  }, []);

  useEffect(() => {
    const defaultNamespace = namespaces.find(
      (namespace) => namespace.is_default
    );
    if (defaultNamespace) {
      setSelectedFolder(defaultNamespace);
    }
  }, []);

  return (
    <div className="flex flex-col mt-2 space-x-1 w-full items-start bg-slate-900 pb-3">
      <div className="flex flex-row w-full">
        <h3 className="font-bold text-sm mx-1">Review your upload</h3>
        <div className="ml-auto flex-none">
          <CancelButton />
        </div>
      </div>
      <hr />
      <span className="text-sm text-blue-300">
        {simplur`${tentativeShapes.length} shape[|s]`}{" "}
        <span
          className="text-blue-300 underline decoration-dashed cursor-zoom-in"
          onClick={() => snapToBounds({ category: "tentative" })}
        >
          (Zoom)
        </span>
      </span>
      <NamespaceSection
        selectedFolder={selectedFolder}
        setSelectedFolder={setSelectedFolder}
      />
      <div className="flex flex-col w-[98%]">
        <SaveButton selectedFolder={selectedFolder} />
      </div>
    </div>
  );
};
