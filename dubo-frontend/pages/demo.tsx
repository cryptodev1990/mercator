import { useState } from "react";

import DemoInfo from "../components/demo-info";
import DuboPreview from "../components/dubo-preview";

const DemoPage = () => {
  const [includeSample, setIncludeSample] = useState(false);
  return (
    <div>
      <div className="max-w-5xl m-auto flex justify-between items-center">
        <div>
          <p className="text-lg mr-3">
            Select a data set (or upload your own) then ask a question.
          </p>
          <div className="text-sm mt-1">
            <input
              type="checkbox"
              checked={includeSample}
              onChange={() => setIncludeSample(!includeSample)}
            />{" "}
            Include data sample for improved accuracy
          </div>
        </div>
        <DemoInfo />
      </div>
      <br />
      <DuboPreview includeSample={includeSample} />
    </div>
  );
};

export default DemoPage;
