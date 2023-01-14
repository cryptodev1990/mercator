import DuboPreview from "../lib/dubo-preview";
import Navbar from "../lib/navbar";

const DemoPage = () => {
  return (
    <>
      <Navbar />
      <br />
      <div>
        <div className="flex flex-col max-w-2xl justify-center m-auto">
          <h1 className="text-2xl">Custom queries</h1>
          <br />
          <p>
            NOTE: We value your privacy. Your data content never leaves the
            browser. We process your data header and a data description but
            otherwise do not see any data itself. Still, because of resource
            constraints, we would recommend processing a smaller (less than
            50MB) data set.
          </p>
          <br />
          <p>
            Dubo is still learning about SQL and won{"'"}t always get the right
            results. With fine-tuning, we can adjust to your data, though this
            is our paid product and it may not be a fit for your company or use
            case.
          </p>
        </div>
        <br />
        <div className="flex row mx-auto justify-center w-full">
          <DuboPreview />
        </div>
      </div>
    </>
  );
};

export default DemoPage;
