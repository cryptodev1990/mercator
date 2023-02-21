import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import clsx from "clsx";

import DemoInfo from "../components/demo-info";
import DuboPreview from "../components/dubo-preview";
import DataSetModal from "../components/data-set-modal";
import { DATA_OPTIONS } from "../lib/demo-data";

const DemoPage = () => {
  const router = useRouter();
  const dataQueryParam = router?.query?.data;
  const [isDataSetModalOpen, setIsDataSetModalOpen] = useState(false);
  const [includeSample, setIncludeSample] = useState(false);
  const [customData, setCustomData] = useState<File[] | null>(null);
  const [selectedData, setSelectedData] = useState<SampleDataKey | null>(null);
  const [urlsOrFile, setUrlsOrFile] = useState<(string | File)[] | null>(null);
  const [dataSetName, setDataSetName] = useState<string | null>(null);

  useEffect(() => {
    if (dataQueryParam === "census" || dataQueryParam === "fortune500") {
      setSelectedData(dataQueryParam);
      setIsDataSetModalOpen(false);
    } else {
      setIsDataSetModalOpen(true);
    }
  }, [dataQueryParam]);

  useEffect(() => {
    if (customData) {
      setUrlsOrFile(customData);
      setDataSetName(customData[0].name);
      setSelectedData(null);
    }
  }, [customData]);

  useEffect(() => {
    if (selectedData) {
      setUrlsOrFile(DATA_OPTIONS[selectedData].data);
      setDataSetName(DATA_OPTIONS[selectedData].label);
      setCustomData(null);
    }
  }, [selectedData]);

  return (
    <div>
      <div className="max-w-5xl m-auto mb-6 flex flex-col justify-between items-start gap-3 md:flex-row md:items-center">
        <div
          className={clsx(
            "transition flex flex-col sm:flex-row gap-4",
            !urlsOrFile ? "opacity-0" : "opacity-100"
          )}
        >
          <button
            className="px-2 sm:px-4 py-2 border border-spBlue text-md w-max cursor-pointer transition duration-300 ease bg-spBlue text-white hover:shadow-lg"
            onClick={() => setIsDataSetModalOpen(true)}
          >
            {dataSetName}
          </button>
          <div
            className="text-sm select-none cursor-pointer flex items-center"
            onClick={() => setIncludeSample(!includeSample)}
          >
            <input
              type="checkbox"
              checked={includeSample}
              className="mr-2"
              onChange={() => setIncludeSample(!includeSample)}
            />{" "}
            Include data sample for improved accuracy
          </div>
        </div>
        <div className="flex gap-2 self-start">
          <DataSetModal
            isOpen={isDataSetModalOpen}
            setIsOpen={setIsDataSetModalOpen}
            setCustomData={setCustomData}
            setSelectedData={setSelectedData}
            selectedData={selectedData}
            urlsOrFile={urlsOrFile}
          />
          <div
            className={clsx(
              "transition",
              !urlsOrFile ? "opacity-0" : "opacity-100"
            )}
          >
            <DemoInfo />
          </div>
        </div>
      </div>
      {urlsOrFile && (
        <DuboPreview
          includeSample={includeSample}
          urlsOrFile={urlsOrFile}
          selectedData={selectedData}
        />
      )}
    </div>
  );
};

export default DemoPage;
