import { useEffect, useRef, Dispatch, SetStateAction } from "react";
import clsx from "clsx";

import { DATA_OPTIONS } from "../lib/demo-data";
import { getFileFromUpload } from "../lib/utils";

const DataSetModal = ({
  isOpen,
  setIsOpen,
  setCustomData,
  selectedData,
  setSelectedData,
  urlsOrFile,
}: {
  isOpen: boolean;
  setIsOpen: Dispatch<SetStateAction<boolean>>;
  setCustomData: Dispatch<SetStateAction<File[] | null>>;
  setSelectedData: Dispatch<SetStateAction<SampleDataKey | null>>;
  selectedData: SampleDataKey | null;
  urlsOrFile: (string | File)[] | null;
}) => {
  const modalRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        modalRef.current &&
        event.target &&
        !modalRef.current.contains(event.target as Node) &&
        urlsOrFile
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [modalRef, urlsOrFile]);

  return (
    <>
      <div className="flex items-center gap-4">
        <button
          type="button"
          className={clsx(
            "inline-block px-3 py-2 border border-spBlue text-spBlue font-medium text-md leading-tight hover:bg-gray-100 focus:bg-gray-100 transition duration-150 ease-in-out",
            !urlsOrFile ? "opacity-0" : "opacity-100"
          )}
          onClick={() => setIsOpen(true)}
        >
          Change Data Set
        </button>
      </div>

      <div
        className={clsx(
          "modal fade fixed top-0 left-0 w-full h-full outline-none overflow-x-hidden overflow-y-auto",
          isOpen ? "show" : "invisible"
        )}
        onAnimationEnd={(e) => console.log("onAnimationStart")}
      >
        <div className="modal-dialog modal-dialog-centered relative w-auto pointer-events-none">
          <div
            ref={modalRef}
            className="modal-content border-none shadow-lg relative flex flex-col w-full pointer-events-auto bg-white bg-clip-padding outline-none text-current"
          >
            {urlsOrFile && (
              <button
                className="btn-close box-content w-6 h-6 text-black text-sm border-none rounded-none opacity-50 hover:text-black hover:opacity-75 hover:no-underline absolute right-4 top-4 hover:cursor-pointer z-[1100]"
                onClick={() => setIsOpen(false)}
              />
            )}
            <div className="modal-body relative p-8 flex flex-col items-center gap-6">
              <h5
                className="text-2xl font-medium leading-normal text-gray-800 text-center"
                id="datasetModalLabel"
              >
                Welcome to <span className="text-spBlue font-bold">dubo</span>
              </h5>
              <p className="leading-5 text-center">
                Choose one of our sample data sets:
              </p>

              <div className="flex flex-col gap-2 justify-center items-center">
                {Object.keys(DATA_OPTIONS).map((key) => (
                  <button
                    className={clsx(
                      "px-2 sm:px-4 py-2 rounded-full border border-spBlue text-sm w-max cursor-pointer sm:truncate sm:text transition",
                      "hover:border-spBlue hover:text-spBlue hover:bg-white",
                      selectedData === key
                        ? "bg-white text-spBlue"
                        : "bg-spBlue text-white"
                    )}
                    key={key}
                    onClick={() => {
                      setSelectedData(key as SampleDataKey);
                      setIsOpen(false);
                    }}
                  >
                    {DATA_OPTIONS[key as SampleDataKey].label}
                  </button>
                ))}
              </div>

              <p className="text-center">or</p>

              <div className="flex flex-col items-center gap-2">
                <button
                  className="inline-block px-3 py-2 border border-white bg-spBlue hover:border-spBlue hover:text-spBlue hover:bg-white border-spBlue text-white font-medium text-md leading-tight hover:bg-white focus:outline-none focus:ring-0 transition"
                  onClick={async (e) => {
                    const file = await getFileFromUpload();
                    if (file) {
                      setCustomData([file]);
                      setIsOpen(false);
                    }
                  }}
                >
                  Upload your own data set
                </button>

                <div className="text-gray-500 text-xs">
                  .csv and .json are accepted
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div
        className={clsx("modal-backdrop fade", isOpen ? "show" : "invisible")}
      />
    </>
  );
};

export default DataSetModal;
