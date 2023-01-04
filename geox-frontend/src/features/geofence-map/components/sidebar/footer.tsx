import { useGetNamespaces } from "features/geofence-map/hooks/use-openapi-hooks";
import Loading from "react-loading";
import simplur from "simplur";
import { useShapes } from "../../hooks/use-shapes";
import { AddButton } from "./shape-list-tab/namespace-section/add-button";

export const Footer = () => {
  const { numShapes } = useShapes();
  const { data: namespaces } = useGetNamespaces();

  return (
    <footer className="flex flex-col mt-auto bg-slate-800">
      <div className="bg-slate-600 border border-slate-200">
        <AddButton />
      </div>
      <p className="text-xs m-1">
        {
          <>
            {simplur`${numShapes || 0} shape[|s] in ${
              namespaces ? namespaces.length : 0
            } folder[|s]`}
          </>
        }
      </p>
    </footer>
  );
};
