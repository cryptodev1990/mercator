import { useDispatch } from "react-redux";
import { IntentResponse } from "src/store/search-api";

const ZoomButton = ({ searchResult }: { searchResult: IntentResponse }) => {
  const dispatch = useDispatch();
  function onClick() {
    alert("zoom to " + searchResult?.query);
  }
  return (
    <button
      className="bg-slate-200 hover:bg-slate-300 text-slate-800 font-bold py-2 px-4 rounded"
      onClick={onClick}
    >
      Z
    </button>
  );
};

export default ZoomButton;
