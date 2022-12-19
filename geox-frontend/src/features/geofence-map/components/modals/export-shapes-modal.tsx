import { useEffect, useState } from "react";
import { DownloadIcon } from "../../../../common/components/icons";
import { useGetAllShapes } from "../../hooks/use-openapi-hooks";
import { useShapes } from "../../hooks/use-shapes";
import { useUiModals } from "../../hooks/use-ui-modals";
import { UIModalEnum } from "../../types";
import { geoShapesToFeatureCollection } from "../../utils";
import { ModalCard } from "./modal-card";
import { topology } from "topojson-server";
import ControlledDropdown from "common/components/ControlledDropdown";

const formatOptions = [
  { key: "geojson", label: "GeoJSON" },
  { key: "topojson", label: "TopoJSON" },
];

export const ExportShapesModal = () => {
  const { modal, closeModal } = useUiModals();
  const { numShapes } = useShapes();
  const limit = useState(20)[0];
  const offset = useState(0)[0];
  const { data } = useGetAllShapes(limit, offset);
  const [exportable, setExportable] = useState<any>();
  const [selectedFormat, setSelectedFormat] = useState(formatOptions[0]);

  useEffect(() => {
    if (data) {
      setExportable(geoShapesToFeatureCollection(data));
    }
  }, [data]);

  return (
    <ModalCard
      isLoading={exportable ? false : true}
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
      <div className="text-black">
        <p>
          Export your shapes to a flat file, like GeoJSON or TopoJSON. You have{" "}
          <b>{numShapes}</b> shapes defined.
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
        <div className="flex pt-2">
          <div className="text-black mr-4">Select Export Format:</div>
          <ControlledDropdown
            options={formatOptions}
            handleOptionSelect={setSelectedFormat}
            selectedOption={selectedFormat}
          />
        </div>
      </div>
    </ModalCard>
  );
};
