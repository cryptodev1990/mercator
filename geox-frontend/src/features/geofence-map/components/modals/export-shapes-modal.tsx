import { useEffect, useState } from "react";
import { DownloadIcon } from "../../../../common/components/icons";
import { useShapes } from "../../hooks/use-shapes";
import { useUiModals } from "../../hooks/use-ui-modals";
import { UIModalEnum } from "../../types";
import { geoShapesToFeatureCollection } from "../../utils";
import { ModalCard } from "./modal-card";
import { topology } from "topojson-server";
import ControlledDropdown from "common/components/ControlledDropdown";
import { GeofencerService } from "client";
import toast from "react-hot-toast";

const formatOptions = [
  { key: "geojson", label: "GeoJSON" },
  { key: "topojson", label: "TopoJSON" },
];

export const ExportShapesModal = () => {
  const { modal, closeModal } = useUiModals();
  const { numShapes } = useShapes();
  const [selectedFormat, setSelectedFormat] = useState(formatOptions[0]);
  const [selectedNamespace, setSelectedNamespace] = useState({
    key: "all",
    label: "All Namespaces",
    id: "all",
  });
  const { namespaces } = useShapes();

  return (
    <ModalCard
      open={modal === UIModalEnum.ExportShapesModal}
      onClose={closeModal}
      onSubmit={async () => {
        closeModal();

        const loadingToastID = toast.loading("Downloading Namespace...");
        const data = await GeofencerService.getShapesGeofencerShapesGet(
          selectedNamespace.id === "all" ? undefined : selectedNamespace.id, // namespace
          undefined, // user
          undefined // offset
        );

        const exportable: any = geoShapesToFeatureCollection(data);
        const exportData =
          selectedFormat.key === "geojson"
            ? exportable
            : topology({ exportable });

        console.log("exportData", exportData);
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
        toast.dismiss(loadingToastID);
        toast.success("Namespace downloading completed");
      }}
      icon={
        <DownloadIcon className="h-6 w-6 text-green-600" aria-hidden="true" />
      }
      title="Download shapes"
    >
      <div className="text-black ">
        <p>
          Export your shapes to a flat file, like GeoJSON or TopoJSON. You have{" "}
          <b>{numShapes}</b> shapes defined.
        </p>
        <br />

        <div className="grid grid-cols-12 gap-2 content-start">
          <div className="col-span-5 text-black">Select Format:</div>
          <div className="col-span-4">
            {" "}
            <ControlledDropdown
              options={formatOptions}
              handleOptionSelect={setSelectedFormat}
              selectedOption={selectedFormat}
            />
          </div>
          <div className="col-span-3"></div>
          <div className="col-span-5 text-black">Select Namespace:</div>
          <div className="col-span-4">
            <ControlledDropdown
              options={[
                ...namespaces.map((namespace) => ({
                  key: namespace.slug,
                  label: namespace.name,
                  id: namespace.id,
                })),
                { key: "all", label: "All Namespaces" },
              ]}
              handleOptionSelect={setSelectedNamespace}
              selectedOption={selectedNamespace}
            />
          </div>
          <div className="col-span-3"></div>
        </div>
      </div>
    </ModalCard>
  );
};
