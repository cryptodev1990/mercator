import { useEffect, useState } from "react";
import { CancelIcon, DownloadIcon } from "../../../../common/components/icons";
import { useGetAllShapes } from "../../hooks/use-openapi-hooks";
import { useShapes } from "../../hooks/use-shapes";
import { useUiModals } from "../../hooks/use-ui-modals";
import { UIModalEnum } from "../../types";
import { geoShapesToFeatureCollection } from "../../utils";
import { ModalCard } from "./modal-card";
import { topology } from "topojson-server";
import { BiCaretDown } from "react-icons/bi";
import clsx from "clsx";

export const ExportShapesModal = () => {
  const { modal, closeModal } = useUiModals();
  const { numShapes } = useShapes();
  const limit = useState(20)[0];
  const offset = useState(0)[0];
  const { data } = useGetAllShapes(limit, offset);
  const [exportable, setExportable] = useState<any>();
  const [selectedFormat, setSelectedFormat] = useState("Geojson");

  const handleOptionSelect = (option: string) => {
    setSelectedFormat(option);
  };

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
        if (selectedFormat === "Geojson") {
          const dataStr =
              "data:text/json;charset=utf-8," +
              encodeURIComponent(JSON.stringify(exportable)),
            downloadAnchorNode = document.createElement("a");
          downloadAnchorNode.setAttribute("href", dataStr);
          downloadAnchorNode.setAttribute("download", "data.geojson");
          document.body.appendChild(downloadAnchorNode); // required for firefox
          downloadAnchorNode.click();
          downloadAnchorNode.remove();
        }

        if (selectedFormat === "Topojson") {
          const exportData = topology({ exportable });
          const dataStr =
              "data:text/json;charset=utf-8," +
              encodeURIComponent(JSON.stringify(exportData)),
            downloadAnchorNode = document.createElement("a");
          downloadAnchorNode.setAttribute("href", dataStr);
          downloadAnchorNode.setAttribute("download", "data.topojson");
          document.body.appendChild(downloadAnchorNode); // required for firefox
          downloadAnchorNode.click();
          downloadAnchorNode.remove();
        }

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
        <FileFormatSelection
          options={["Geojson", "Topojson"]}
          handleOptionSelect={handleOptionSelect}
          initialOption="Geojson"
        />
      </div>
    </ModalCard>
  );
};

// dropdown of the current namespaces
const FileFormatSelection = ({
  options,
  handleOptionSelect,
  initialOption,
}: any) => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [selectedOption, setSelectedOption] = useState(initialOption);

  const handleDropdownClick = () => {
    setIsDropdownOpen(!isDropdownOpen);
  };

  return (
    <div className="flex flex-row items-center">
      <div className="flex flex-row items-center">
        <p className="text-black text-sm mr-2">Select Format</p>
        <div className="flex flex-row items-center">
          <div
            className="flex flex-row items-center justify-center bg-white rounded w-full h-8 m-2 p-2"
            onClick={handleDropdownClick}
          >
            <BiCaretDown className="fill-black" />
            <p
              className={clsx({
                ["text-black text-sm"]: true,
                ["opacity-50"]: selectedOption,
              })}
            >
              {selectedOption || "Select Format"}{" "}
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
              {options.map((option: string) => (
                <div
                  className="flex flex-row items-center justify-start w-full h-8 rounded-md cursor-pointer hover:bg-gray-200 p-2"
                  onClick={() => {
                    setSelectedOption(option);
                    handleOptionSelect(option);
                  }}
                >
                  <p className="text-black text-sm">{option}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
