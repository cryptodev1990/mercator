import { useRouter } from "next/router";
import { CloseButton } from "../close-button";
import { TitleBlock } from "./title-block";

export const DataCatalogContent = ({}: {}) => {
  const router = useRouter();

  return (
    <div className="mt-3 relative pt-3 border border-purple-500 animate-fadeIn500">
      <TitleBlock zoomThreshold={false} />
      <div className="relative float-right border border-red-500">
        <CloseButton onClick={() => router.push("/demos/census")} />
      </div>
      <div>
        <div className="p-2">
          <h1 className="text-xl font-bold">Data Catalog</h1>
          <p className="text-sm">
            All the variables from the US Census Bureau{"'"}s 2022 5-year
            American Community Survey (ACS) made available by dubo.
          </p>
        </div>
      </div>
    </div>
  );
};
