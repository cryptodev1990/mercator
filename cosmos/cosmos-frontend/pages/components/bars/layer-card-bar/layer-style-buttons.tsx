import simplur from "simplur";
import { IntentResponse } from "src/store/search-api";
import ZoomButton from "./buttons/zoom-button";
import ColorPicker from "./buttons/color-picker";
import { LayerStyle, updateStyle } from "src/shapes/shape-slice";
import { useDispatch } from "react-redux";
import { deleteOneSearchResult } from "src/search/search-slice";
import { convertHexToRGB } from "src/lib/colors";
import RadiusPicker from "./buttons/radius-picker";
import SliderPicker from "./buttons/slider-picker";

const DeleteButton = ({ searchResult }: { searchResult: IntentResponse }) => {
  const dispatch = useDispatch();
  function onClick() {
    dispatch(deleteOneSearchResult(searchResult?.query));
  }
  return (
    <button
      className="bg-slate-200 hover:bg-slate-300 text-slate-800 font-bold py-2 px-4 rounded"
      onClick={onClick}
    >
      Delete
    </button>
  );
};

const LayerStyleButtons = ({
  ir,
  layerStyle,
}: {
  ir: IntentResponse;
  layerStyle: LayerStyle;
}) => {
  const dispatch = useDispatch();
  const numResults = ir?.parse_result.geom?.features?.length ?? 0;
  return (
    <div className="flex flex-row">
      <p>{simplur`${numResults} shape[|s]`}</p>
      <ZoomButton searchResult={ir} />
      <ColorPicker
        color={layerStyle?.paint ?? []}
        setColor={(newColor: string) => {
          if (!newColor) {
            return;
          }
          dispatch(
            updateStyle({
              paint: convertHexToRGB(newColor),
              id: layerStyle?.id,
            })
          );
        }}
      />
      <RadiusPicker
        radius={layerStyle?.lineThicknessPx ?? 0}
        setRadius={(newKnotSize: number) => {
          dispatch(
            updateStyle({ lineThicknessPx: newKnotSize, id: layerStyle.id })
          );
        }}
      />
      <SliderPicker
        knotSize={layerStyle?.opacity}
        min={0}
        step={"0.1"}
        max={1}
        setKnotSize={(newOpacity: number) => {
          dispatch(updateStyle({ opacity: newOpacity, id: layerStyle.id }));
        }}
      />
      <DeleteButton searchResult={ir} />
    </div>
  );
};

export default LayerStyleButtons;
