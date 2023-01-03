import { LayerStyle } from "src/shapes/shape-slice";
import { IntentResponse } from "src/store/search-api";
import ColorSquare from "./buttons/color-square";

const LayerCard = ({
  searchResult,
  layerStyle,
  onClick,
}: {
  searchResult: IntentResponse;
  layerStyle: LayerStyle;
  onClick: () => void;
}) => {
  const query = searchResult?.query;

  if (!query) {
    return null;
  }

  return (
    <div
      onClick={() => {
        onClick();
      }}
      onMouseEnter={() => {
        console.log("hovered");
      }}
      className="flex flex-row w-64 bg-slate-100 text-slate-800 shadow-lg p-2 cursor-pointer"
    >
      <h4 className="font-bold text-ellipsis">{query}</h4>
      <div className="flex-none ml-auto">
        <ColorSquare color={layerStyle?.paint || []} />
      </div>
    </div>
  );
};

export default LayerCard;
