import { useRouter } from "next/router";

import Demos from "../../components/demos";
import DemoInfo from "../../components/demo-info";

const DemoPage = () => {
  const router = useRouter();
  const { databaseSchema } = router.query;

  if (
    typeof databaseSchema === "string" &&
    databaseSchema !== "polygon-blocks" &&
    databaseSchema !== "bitcoin-blocks" &&
    databaseSchema !== "ethereum-blocks"
  ) {
    router.push(`/demo`);
  }

  return (
    <div>
      <div className="max-w-5xl m-auto flex justify-between items-center">
        <p className="text-lg mr-3">
          Ask a question about the {databaseSchema} data set.
        </p>
        <DemoInfo />
      </div>
      <br />
      <Demos databaseSchema={databaseSchema as DatabaseSchema} />
    </div>
  );
};

export default DemoPage;
