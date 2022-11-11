import React, { useCallback, useEffect, useState } from "react";
import { DropEvent, FileRejection, useDropzone } from "react-dropzone";
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
  const [isUploading, setIsUploading] = useState(false);

  const {
    fetchGeoJson,
    geojson,
    loading,
    error,
    convertJsonFileToGeojson,
    initialUploadSize,
  } = useConvertedGeojson();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    acceptedFiles.forEach((file) => {
      if (file.name.endsWith("json")) {
        const opts: any = {};
        convertJsonFileToGeojson(file, opts);
      } else {
        fetchGeoJson(file);
      }
    });
    setFiles(acceptedFiles);
  }, []);

  const { getRootProps, getInputProps } = useDropzone({
    useFsAccessApi: false,
    onDrop,
    onDropRejected: (fileRejection: FileRejection[], event: DropEvent) => {
      console.error(event);
      toast.error("Error with file upload, please try again");
    },
  });

  useEffect(() => {
    if (error) {
      toast.error(error);
      setFiles([]);
    }
  }, [error]);

  useEffect(() => {
    if (geojson && isUploading) {
      const prospects = geojson.map((feature) => {
        return {
          geojson: feature,
        };
      });
      setTentativeShapes(prospects);
      setIsUploading(false);
      closeModal();
    }
  }, [geojson, isUploading]);

  function onPublish() {
    setIsUploading(true);
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
        loading={loading || isUploading}
      ></UploadModalView>
    </div>
  );
};
