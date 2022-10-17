import { useShapes } from "../../../hooks/use-shapes";
import { useViewport } from "../../../hooks/use-viewport";
import { BiAddToQueue } from "react-icons/bi";
import { VscJson } from "react-icons/vsc";
import { AiFillDatabase } from "react-icons/ai";
import Loading from "react-loading";
import { useUiModals } from "../../../hooks/use-ui-modals";
import { UIModalEnum } from "../../../types";
import { useDbSync } from "../../../hooks/use-db-sync";
import { useSelectedShapes } from "../../../hooks/use-selected-shapes";
import { NamespaceSection } from "./namespace-section";
import simplur from "simplur";

const EmptyMessage = () => {
  return (
    <div className="flex flex-col justify-center h-full p-3">
      <p className="text-white text-left">
        No shapes have been added to the map yet.
      </p>
      <br />
      <p className="text-white text-left">
        Click the{" "}
        <span className="inline-flex">
          <BiAddToQueue />
        </span>{" "}
        button to add shapes.
      </p>
    </div>
  );
};

const TentativeButtonBank = () => {
  // Button bank that pops up for uploaded shapes or shapes from the command palette
  const { snapToCentroid } = useViewport();
  const { tentativeShapes, setTentativeShapes, bulkAddShapes, updateLoading } =
    useShapes();
  const { clearSelectedShapeUuids } = useSelectedShapes();
  return (
    <div className="mt-2 space-x-1">
      <p className="font-bold text-xs mx-1">External data</p>
      <hr />
      <h3 className="font-bold uppercase text-sm text-blue-300">
        {tentativeShapes.length} shapes in queue
      </h3>
      <button
        className="btn btn-xs bg-blue-400 text-white rounded-none"
        disabled={updateLoading}
        onClick={() => {
          bulkAddShapes(
            tentativeShapes.map((shape) => ({
              ...shape,
            })),
            {
              onSuccess: () => {
                snapToCentroid({ category: "tentative" });
                setTentativeShapes([]);
                clearSelectedShapeUuids();
              },
            }
          );
        }}
      >
        + Publish
      </button>
      <button
        className="btn btn-xs bg-blue-400 text-white rounded-none"
        onClick={() => snapToCentroid({ category: "tentative" })}
      >
        Zoom to centroid
      </button>
      <button
        className="btn btn-xs bg-blue-400 text-white rounded-none"
        onClick={() => setTentativeShapes([])}
      >
        Clear
      </button>
    </div>
  );
};

export const ShapeBarPaginator = () => {
  const {
    shapeMetadata,
    tentativeShapes,
    numShapes,
    namespaces,
    shapeMetadataIsLoading,
    shapeMetadataError,
  } = useShapes();
  const { openModal } = useUiModals();
  const { isLoading: isPolling } = useDbSync();

  return (
    <div className="flex flex-col">
      <div className="bg-slate-700 flex flex-row justify-between cursor-pointer">
        {[
          {
            icon: <BiAddToQueue className="fill-white" />,
            disabled: false,
            onClick: () => openModal(UIModalEnum.UploadShapesModal),
            text: "Upload",
            title: "Upload a GeoJSON or other shape file",
          },
          {
            icon: <VscJson className="fill-white" size={15} />,
            disabled: numShapes === 0,
            title: "Export shapes as GeoJSON",
            onClick: () => openModal(UIModalEnum.ExportShapesModal),
            text: "Export",
          },
          {
            icon: isPolling ? (
              <Loading className="spin" height={20} width={20} />
            ) : (
              <AiFillDatabase className="fill-white" />
            ),
            title: "Publish shapes to your Snowflake or Redshift database",
            disabled: isPolling || numShapes === 0,
            onClick: () => {
              if (isPolling) return;
              openModal(UIModalEnum.DbSyncModal);
            },
            text: "DB Sync",
          },
        ].map((button, i) => (
          <button
            key={i}
            disabled={button.disabled}
            className="btn btn-xs h-10 rounded-none bg-slate-700 text-white space-x-1 grow"
            onClick={button.onClick}
          >
            {button.icon}{" "}
            <label className="cursor-pointer">{button.text}</label>
          </button>
        ))}
      </div>
      {tentativeShapes.length > 0 && <TentativeButtonBank />}
      {namespaces.length !== 0 && <NamespaceSection />}
      {!shapeMetadataIsLoading &&
        shapeMetadata.length === 0 &&
        namespaces.length === 0 &&
        shapeMetadataError === null && <EmptyMessage />}
      {shapeMetadataError && (
        <div className="flex flex-col justify-center h-full p-3">
          <p className="text-white text-left">
            There was an error loading shapes.
          </p>
          <br />
          <p className="text-white text-left">
            Please refresh the page and try again.
          </p>
        </div>
      )}
      <footer className="flex flex-col">
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
    </div>
  );
};
