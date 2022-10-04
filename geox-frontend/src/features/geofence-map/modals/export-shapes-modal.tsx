import { useEffect, useState } from "react";
import { BiDownload } from "react-icons/bi";
import { useGetAllShapes } from "../hooks/openapi-hooks";
import { useShapes } from "../hooks/use-shapes";
import { useUiModals } from "../hooks/use-ui-modals";
import { UIModalEnum } from "../types";
import { geoShapesToFeatureCollection } from "../utils";
import { ModalCard } from "./modal-card";

export const ExportShapesModal = () => {
  const { modal, closeModal } = useUiModals();
  const { numShapes, numShapesIsLoading } = useShapes();
  const [limit, setLimit] = useState(20);
  const [offset, setOffset] = useState(0);
  const { data, isFetching } = useGetAllShapes(limit, offset);
  const [exportable, setExportable] = useState<any>();

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
        const dataStr =
            "data:text/json;charset=utf-8," +
            encodeURIComponent(JSON.stringify(exportable)),
          downloadAnchorNode = document.createElement("a");
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", "data.json");
        document.body.appendChild(downloadAnchorNode); // required for firefox
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
        closeModal();
      }}
      icon={
        <BiDownload className="h-6 w-6 text-green-600" aria-hidden="true" />
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
      </div>
    </ModalCard>
  );
};
