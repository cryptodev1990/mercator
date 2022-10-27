import { useCallback, useEffect, useState } from "react";
import { useDropzone } from "react-dropzone";
import toast from "react-hot-toast";
import { useShapes } from "../../../hooks/use-shapes";

import { DropZone } from "./drop-zone";
import { useConvertedGeojson } from "./use-converted-geojson";
import { UploadModalView } from "./upload-modal-view";
import { useUiModals } from "../../../hooks/use-ui-modals";

export const UploadModal = () => {
  const { setTentativeShapes } = useShapes();
  const [files, setFiles] = useState<File[]>([]);
  const { modal, closeModal } = useUiModals();

  const { fetchGeoJson, geojson, loading, error, convertJsonFileToGeojson } =
    useConvertedGeojson();

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      acceptedFiles.forEach((file) => {
        if (file.name.endsWith("json")) {
          const opts: any = {};
          convertJsonFileToGeojson(file, opts);
        } else {
          fetchGeoJson(file);
        }
      });
      setFiles(acceptedFiles);
    },
    [fetchGeoJson, convertJsonFileToGeojson]
  );

  const { getRootProps, getInputProps } = useDropzone({
    useFsAccessApi: false,
    onDrop,
    onDropRejected: (e: any) => {
      console.error(e);
      toast.error("Error with file upload, please try again");
    },
  });

  useEffect(() => {
    if (error) {
      toast.error(error);
      setFiles([]);
    }
  }, [error]);

  function onPublish() {
    const prospects = geojson.map((feature) => {
      return {
        geojson: feature,
        name: feature.properties?.name ?? "New upload",
        //name: feature.properties?.name || "New upload",
      };
    });
    setTentativeShapes(prospects);
    closeModal();
  }

  return (
    <div>
      <UploadModalView
        enabled={files.length > 0}
        onPublish={onPublish}
        open={modal === "UploadShapesModal"}
        close={closeModal}
        dropzone={
          <DropZone
            getRootProps={getRootProps}
            getInputProps={getInputProps}
            files={files}
            setFiles={setFiles}
            loading={loading}
          />
        }
        loading={loading}
      ></UploadModalView>
    </div>
  );
};
