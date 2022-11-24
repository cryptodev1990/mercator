import Loading from "react-loading";
import simplur from "simplur";
import { useShapes } from "../../hooks/use-shapes";
import { AddButton } from "./shape-list-tab/namespace-section/add-button";

export const Footer = () => {
  const { shapeMetadataIsLoading, numShapes, namespaces } = useShapes();
  return (
    <footer className="flex flex-col mt-auto bg-slate-800">
      <div className="bg-slate-600 border border-slate-200">
        <AddButton />
      </div>
      <p className="text-xs m-1">
        {shapeMetadataIsLoading && (
          <Loading className="spin" height={20} width={20} />
        )}
        {
          <>
            {simplur`${numShapes || 0} shape[|s] in ${
              namespaces.length
            } folder[|s]`}
          </>
        }
      </p>
    </footer>
  );
};
