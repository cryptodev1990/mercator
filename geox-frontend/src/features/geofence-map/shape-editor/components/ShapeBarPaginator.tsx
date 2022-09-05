import { useShapes } from "../../hooks/use-shapes";
import { useViewport } from "../../hooks/use-viewport";
import { ShapeCard } from "./shape-card";
import {
  useBulkAddShapesMutation,
  usePollCopyTaskQuery,
  useTriggerCopyTaskMutation,
} from "../../hooks/openapi-hooks";
import { BiAddToQueue, BiLeftArrow, BiRightArrow } from "react-icons/bi";
import { VscJson } from "react-icons/vsc";
import { AiFillDatabase } from "react-icons/ai";
import { useEffect, useState } from "react";
import { TasksService } from "../../../../client";
import toast from "react-hot-toast";
import Loading from "react-loading";

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

const NUM_SHAPE_CARDS = 15;

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

export const ShapeBarPaginator = ({ setUploadModalOpen }: any) => {
  const { shapes, tentativeShapes } = useShapes();
  const [page, setPage] = useState(0);

  const {
    data: triggerData,
    isLoading,
    mutate: triggerCopyTask,
  } = useTriggerCopyTaskMutation();
  const { data: numShapes, isLoading: isPolling } = usePollCopyTaskQuery(
    triggerData?.task_id
  );

  const loading = isLoading || isPolling;

  // Feature: Display card for each shape in the namespace
  const shapeCards = shapes
    ?.filter((shape, i) => i < NUM_SHAPE_CARDS)
    .map((shape, i) => <ShapeCard shape={shape} key={i} />);

  return (
    <div className="flex flex-col">
      <div className="bg-slate-700 flex flex-row justify-between px-1">
        {[
          {
            icon: <BiAddToQueue className="fill-white" />,
            disabled: false,
            onClick: () => setUploadModalOpen(true),
            text: "Upload",
          },
          {
            icon: <VscJson className="fill-white" size={15} />,
            disabled: false,
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
            icon: loading ? (
              <Loading className="spin" height={20} width={20} />
            ) : (
              <AiFillDatabase className="fill-white" />
            ),
            disabled: loading,
            onClick: () => {
              triggerCopyTask();
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
            {button.icon} <label>{button.text}</label>
          </button>
        ))}
      </div>
      {tentativeShapes.length > 0 && <TentativeButtonBank />}
      <p className="font-bold text-xs mx-1">Geofences</p>
      <hr />
      {shapes?.length !== 0 ? (
        <div key={1} className="relative h-[80vh]">
          {shapeCards}
        </div>
      ) : (
        <NewUserMessage />
      )}
      <footer className="flex flex-row">
        <button>
          <BiLeftArrow />
        </button>{" "}
        {NUM_SHAPE_CARDS} of {shapes.length}{" "}
        <button>
          <BiRightArrow />
        </button>
      </footer>
    </div>
  );
};
