import DemoInfo from "../components/demo-info";
import DuboPreview from "../components/dubo-preview";

const DemoPage = () => (
  <div>
    <div className="max-w-5xl m-auto flex justify-between items-center">
      <p className="text-lg mr-3">
        Select a data set (or upload your own) then ask a question.
      </p>
      <DemoInfo />
    </div>
    <br />
    <DuboPreview />
  </div>
);

export default DemoPage;
