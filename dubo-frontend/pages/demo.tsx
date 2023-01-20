import DuboPreview from "../lib/dubo-preview";
import Navbar from "../lib/navbar";

const Info = () => {
  return (
    <>
      <button
        type="button"
        className="inline-block px-3 py-2 border border-spBlue text-spBlue font-medium text-md leading-tight hover:bg-black hover:bg-opacity-5 focus:outline-none focus:ring-0 transition duration-150 ease-in-out"
        data-bs-toggle="modal"
        data-bs-target="#disclaimerModal"
      >
        Disclaimer
      </button>
      <div
        className="modal fade fixed top-0 left-0 hidden w-full h-full outline-none overflow-x-hidden overflow-y-auto"
        id="disclaimerModal"
        tabIndex={-1}
        aria-labelledby="disclaimerModalLabel"
        aria-hidden="true"
      >
        <div className="modal-dialog relative w-auto pointer-events-none">
          <div className="modal-content border-none shadow-lg relative flex flex-col w-full pointer-events-auto bg-white bg-clip-padding outline-none text-current">
            <div className="modal-header flex flex-shrink-0 items-center justify-between p-4 border-b border-gray-200">
              <h5
                className="text-xl font-medium leading-normal text-gray-800"
                id="disclaimerModalLabel"
              >
                Disclaimer
              </h5>
              <button
                type="button"
                className="btn-close box-content w-4 h-4 p-1 text-black border-none rounded-none opacity-50 focus:shadow-none focus:outline-none focus:opacity-100 hover:text-black hover:opacity-75 hover:no-underline"
                data-bs-dismiss="modal"
                aria-label="Close"
              ></button>
            </div>
            <div className="modal-body relative p-4">
              <p className="leading-5">
                We value your privacy. Your data content never leaves the
                browser. We process your data header and a data description but
                otherwise do not see any data itself. Still, because of resource
                constraints, we would recommend processing a smaller (less than
                30MB) data set.
              </p>
              <br />
              <p className="leading-5">
                Dubo is still learning about SQL and won{"'"}t always get the
                right results. With fine-tuning, we can adjust to your data,
                though this is our paid product and it may not be a fit for your
                company or use case.
              </p>
            </div>
            <div className="modal-footer flex flex-shrink-0 flex-wrap items-center justify-end p-2 border-t border-gray-200 rounded-b-md">
              <button
                type="button"
                className="inline-block px-3 py-2 bg-transparent text-spBlue font-medium text-md leading-tight hover:text-spBlueDark hover:bg-gray-100 focus:bg-gray-100 focus:outline-none focus:ring-0 active:bg-gray-200 transition duration-150 ease-in-out"
                data-bs-dismiss="modal"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

const DemoPage = () => (
  <>
    <Navbar />
    <div className="pr-8 pl-8 pt-8 pb-16 min-h-full">
      <div className="max-w-5xl m-auto flex justify-between items-center">
        <p className="text-lg mr-3">Choose a data set below to get started:</p>
        <Info />
      </div>
      <br />
      <DuboPreview />
    </div>
  </>
);

export default DemoPage;
