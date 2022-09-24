import { useShapes } from "../../hooks/use-shapes";
import { useViewport } from "../../hooks/use-viewport";
import { ShapeCard } from "./shape-card";
import { useBulkAddShapesMutation } from "../../hooks/openapi-hooks";
import { BiAddToQueue } from "react-icons/bi";
import { VscJson } from "react-icons/vsc";
import { AiFillDatabase } from "react-icons/ai";
import Loading from "react-loading";
import { Virtuoso } from "react-virtuoso";
import { useUiModals } from "../../hooks/use-ui-modals";
import { UIModalEnum } from "../../types";
import { useDbSync } from "../../hooks/use-db-sync";

const NewUserMessage = () => {
  return (
    <div className="p-5 bg-slate-600">
      <p>
        Welcome to{" "}
        <strong
          className="
                  bg-gradient-to-r bg-clip-text  text-transparent 
                  from-white via-porsche to-white
                  animate-text"
        >
          Geofencer
        </strong>
        ! You're part of our private beta.
      </p>
      <br />
      <p>Start adding polygons by clicking on the button bank on the right</p>
    </div>
  );
};

const TentativeButtonBank = () => {
  const { snapToCentroid } = useViewport();
  const { tentativeShapes, setTentativeShapes } = useShapes();
  const { mutate: addShapesBulk } = useBulkAddShapesMutation();

  return (
    <div className="mt-2 space-x-1">
      <p className="font-bold text-xs mx-1">External data</p>
      <hr />
      <h3 className="font-bold uppercase text-sm text-blue-300">
        {tentativeShapes.length} shapes in queue
      </h3>
      <button
        className="btn btn-xs bg-blue-400 text-white rounded-none"
        onClick={() => {
          addShapesBulk(
            tentativeShapes.map((shape) => ({
              ...shape,
            })),
            {
              onSuccess: () => {
                snapToCentroid({ category: "tentative" });
                setTentativeShapes([]);
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
  const { shapes, tentativeShapes, virtuosoRef } = useShapes();
  const { openModal } = useUiModals();
  const { isLoading: isPolling } = useDbSync();

  // Feature: Display card for each shape in the namespace
  const Row = ({ index, style }: any) => {
    return (
      <div key={index}>
        <ShapeCard shape={shapes[index]} />
      </div>
    );
  };

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
            disabled: false,
            title: "Export shapes as GeoJSON",
            onClick: () => {
              const dataStr =
                "data:text/json;charset=utf-8," +
                encodeURIComponent(
                  JSON.stringify(shapes.map((x) => x.geojson))
                );
              const downloadAnchorNode = document.createElement("a");
              downloadAnchorNode.setAttribute("href", dataStr);
              downloadAnchorNode.setAttribute("download", "geofence.json");
              document.body.appendChild(downloadAnchorNode); // required for firefox
              downloadAnchorNode.click();
              downloadAnchorNode.remove();
            },
            text: "Export",
          },
          {
            icon: isPolling ? (
              <Loading className="spin" height={20} width={20} />
            ) : (
              <AiFillDatabase className="fill-white" />
            ),
            title: "Publish shapes to your Snowflake or Redshift database",
            disabled: isPolling,
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
      <p className="font-bold text-xs mx-1">Geofences</p>
      <hr />
      {shapes?.length !== 0 ? (
        <div
          key={1}
          className="relative short-h:60vh md-h:65vh tall-h:h-[70vh]"
        >
          <Virtuoso
            ref={virtuosoRef}
            className="h-full scrollbar-thin scrollbar-thumb-slate-400 scrollbar-track-slate-700"
            totalCount={shapes.length}
            data={shapes}
            itemContent={(index, shape) => <ShapeCard shape={shape} />}
          />
        </div>
      ) : (
        <NewUserMessage />
      )}
      <footer className="flex flex-col">
        <p className="text-xs m-1">
          {shapes.length} of {shapes.length} shapes
        </p>
      </footer>
    </div>
  );
};
