import { useEffect, useState } from "react";
import { CancelIcon, DownloadIcon } from "../../../../common/components/icons";
import { useGetAllShapes } from "../../hooks/use-openapi-hooks";
import { useShapes } from "../../hooks/use-shapes";
import { useUiModals } from "../../hooks/use-ui-modals";
import { UIModalEnum } from "../../types";
import { geoShapesToFeatureCollection } from "../../utils";
import { ModalCard } from "./modal-card";
import { topology } from "topojson-server";
import { BiCaretDown, BiCaretUp } from "react-icons/bi";
import clsx from "clsx";

export const ExportShapesModal = () => {
  const { modal, closeModal } = useUiModals();
  const { numShapes } = useShapes();
  const limit = useState(20)[0];
  const offset = useState(0)[0];
  const { data } = useGetAllShapes(limit, offset);
  const [exportable, setExportable] = useState<any>();
  const [selectedFormat, setSelectedFormat] = useState({
    key: "geojson",
    label: "Geojson",
  });

  useEffect(() => {
    if (data) {
      setExportable(geoShapesToFeatureCollection(data));
    }
  }, [data]);

  return (
    <ModalCard
      open={modal === UIModalEnum.ExportShapesModal}
      onClose={closeModal}
      onSubmit={() => {
        // export data to a json file
        if (!data) {
          return;
        }
        const exportData =
          selectedFormat.key === "geojson"
            ? exportable
            : topology({ exportable });

        const dataStr =
            "data:text/json;charset=utf-8," +
            encodeURIComponent(JSON.stringify(exportData)),
          downloadAnchorNode = document.createElement("a");
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute(
          "download",
          `data.${selectedFormat.key}`
        );
        document.body.appendChild(downloadAnchorNode); // required for firefox
        downloadAnchorNode.click();
        downloadAnchorNode.remove();

        closeModal();
      }}
      icon={
        <DownloadIcon className="h-6 w-6 text-green-600" aria-hidden="true" />
      }
      title="Download shapes"
    >
      <div>
        <p>
          Export your shapes as a GeoJSON file. You have <b>{numShapes}</b>{" "}
          shapes defined.
        </p>
        <br />
        <p>
          <b>Size of exports is currently limited.</b> To export large feature
          collections contact{" "}
          <a className="link link-primary" href="mailto:support@mercator.tech">
            support@mercator.tech
          </a>{" "}
          for developer API access.
        </p>
        <div className="flex p-2">
          <div className="text-black mr-4">Select Export Format:</div>
          <FileFormatSelection
            options={[
              { key: "geojson", label: "Geojson" },
              { key: "topojson", label: "Topojson" },
            ]}
            handleOptionSelect={setSelectedFormat}
            selectedOption={selectedFormat}
          />
        </div>
      </div>
    </ModalCard>
  );
};

// dropdown of the current namespaces
const FileFormatSelection = ({
  options,
  handleOptionSelect,
  selectedOption,
}: any) => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const handleDropdownClick = () => {
    setIsDropdownOpen(!isDropdownOpen);
  };

  return (
    <div>
      <div
        className="flex border p-1 rounded items-center w-24"
        onClick={handleDropdownClick}
      >
        {isDropdownOpen ? (
          <BiCaretUp className="fill-black" />
        ) : (
          <BiCaretDown className="fill-black" />
        )}
        <p
          className={clsx({
            ["text-black text-sm"]: true,
          })}
        >
          {selectedOption.label || "Select Format"}{" "}
        </p>
      </div>
      {isDropdownOpen && (
        <div className="absolute bg-white rounded-md shadow-md w-24">
          {options.map((option: { key: string; label: string }) => (
            <div
              className="flex flex-row items-center justify-start w-full h-8 rounded-md cursor-pointer hover:bg-gray-200 p-2"
              onClick={() => {
                handleOptionSelect(option);
                handleDropdownClick();
              }}
            >
              <p className="text-black text-sm">{option.label}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
