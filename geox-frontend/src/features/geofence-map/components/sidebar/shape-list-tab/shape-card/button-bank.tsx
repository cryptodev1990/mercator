import clsx from "clsx";
import { useEffect, useState } from "react";
import { BiCaretDown, BiSave } from "react-icons/bi";
import { Namespace, NamespaceResponse } from "../../../../../../client";
import { CancelIcon } from "../../../../../../common/components/icons";
import { useSelectedShapes } from "../../../../hooks/use-selected-shapes";
import { useShapes } from "../../../../hooks/use-shapes";
import { useViewport } from "../../../../hooks/use-viewport";
import simplur from "simplur";
import Loading from "react-loading";
import { useGetNamespaces } from "features/geofence-map/hooks/use-openapi-hooks";

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
    bulkAddShapes,
    setVisibleNamespaces,
    clearOptimisticShapeUpdates,
    setTileUpdateCount,
  } = useShapes();

  const { snapToBounds } = useViewport();
  const { clearSelectedShapeUuids } = useSelectedShapes();
  const [locked, setLocked] = useState(false);

  const [uploadProgress, setUploadProgress] = useState(0);

  return (
    <div className="flex flex-row flex-grow">
      <button
        className="
          btn
          w-full
          bg-green-600
          hover:bg-green-800
          text-white
        "
        disabled={locked}
        onClick={() => {
          setLocked(true);
          bulkAddShapes(
            {
              shapes: tentativeShapes.map((shape) => ({
                ...shape,
                namespace: selectedFolder?.id,
              })),
              onUploadProgress: (progressEvent: ProgressEvent) => {
                const { loaded, total } = progressEvent;
                let precentage = Math.floor((loaded * 100) / total);
                if (precentage === 100) setUploadProgress(91);
                else setUploadProgress(precentage);
              },
            },
            {
              onSuccess: () => {
                snapToBounds({ category: "tentative" });
                setTentativeShapes([]);
                // @ts-ignore
                setVisibleNamespaces([selectedFolder]);
                clearSelectedShapeUuids();
                setLocked(false);
                setUploadProgress(100);
                clearOptimisticShapeUpdates();
                // @ts-ignore
                setTileUpdateCount((t) => t + 1);
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
            <BiSave /> Save
          </>
        )}
        {locked && (
          <div className="w-full bg-gray-200 rounded-full dark:bg-gray-700">
            <div
              className="bg-blue-600 text-xs font-medium text-blue-100 text-center p-0.5 leading-none rounded-full"
              style={{ width: `${uploadProgress}%` }}
            >
              {" "}
              {uploadProgress}%
            </div>
          </div>
        )}
      </button>
    </div>
  );
};

// dropdown of the current namespaces
const NamespaceSection = ({ selectedFolder, setSelectedFolder }: any) => {
  const { data: namespaces } = useGetNamespaces();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const handleDropdownClick = () => {
    setIsDropdownOpen(!isDropdownOpen);
  };

  const handleNamespaceClick = (namespace: NamespaceResponse) => {
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
              {namespaces
                ? namespaces.map((namespace: NamespaceResponse) => (
                    <div
                      className="flex flex-row items-center justify-start w-full h-8 rounded-md cursor-pointer hover:bg-gray-200 p-2"
                      onClick={() => handleNamespaceClick(namespace)}
                    >
                      <p className="text-black text-sm">{namespace.name}</p>
                    </div>
                  ))
                : null}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export const TentativeButtonBank = () => {
  // Button bank that pops up for uploaded shapes or shapes from the command palette
  const { tentativeShapes } = useShapes();
  const { data: namespaces } = useGetNamespaces();
  const { snapToBounds } = useViewport();
  const [selectedFolder, setSelectedFolder] = useState<Namespace | null>(null);

  useEffect(() => {
    if (namespaces) {
      const defaultNamespace = namespaces.find(
        (namespace) => namespace.is_default
      );
      if (defaultNamespace) {
        setSelectedFolder(defaultNamespace);
      }
    }
  }, [namespaces]);

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
