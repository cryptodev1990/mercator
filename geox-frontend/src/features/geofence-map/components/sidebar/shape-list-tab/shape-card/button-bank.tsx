import { useSelectedShapes } from "../../../../hooks/use-selected-shapes";
import { useShapes } from "../../../../hooks/use-shapes";
import { useViewport } from "../../../../hooks/use-viewport";

export const TentativeButtonBank = () => {
  // Button bank that pops up for uploaded shapes or shapes from the command palette
  const { snapToCentroid } = useViewport();
  const { tentativeShapes, setTentativeShapes, bulkAddShapes, updateLoading } =
    useShapes();
  const { clearSelectedShapeUuids } = useSelectedShapes();
  return (
    <div className="mt-2 space-x-1">
      <p className="font-bold text-sm mx-1">External data</p>
      <hr />
      <h3 className="text-sm text-blue-300">
        {tentativeShapes.length} areas in queue
      </h3>
      <button
        className="btn btn-xs bg-blue-400 text-white rounded"
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
        className="btn btn-xs bg-blue-400 text-white rounded"
        onClick={() => snapToCentroid({ category: "tentative" })}
      >
        <span role="img" aria-label="magnifying glass">
          🔍
        </span>
        {"    "}
        Zoom
      </button>
      <button
        className="btn btn-xs bg-red-400 text-white rounded"
        onClick={() => setTentativeShapes([])}
      >
        Clear
      </button>
    </div>
  );
};
