import Loading from "react-loading";
import simplur from "simplur";
import { useShapes } from "../../hooks/use-shapes";

export const Footer = () => {
  const { shapeMetadataIsLoading, numShapes, namespaces } = useShapes();
  return (
    <footer className="flex flex-col mt-auto">
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
