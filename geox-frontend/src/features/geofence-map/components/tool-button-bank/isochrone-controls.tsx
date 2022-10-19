import { useContext } from "react";
import { UIContext } from "../../contexts/ui-context";

export const IsochroneControls = () => {
  // a grid of controls for an isochrone api
  // you can select the mode of transit (driving, walking, biking)
  // you can select the time in minutes
  const { isochroneParams, setIsochroneParams } = useContext(UIContext);
  return (
    <div className="grid grid-flow-col gap-0 bg-slate-400">
      <div className="flex flex-col p-3">
        <label htmlFor="isotime" className="text-xs">
          Drive time
        </label>
        <div>
          <input
            onChange={(e) => {
              setIsochroneParams({
                ...isochroneParams,
                timeInMinutes: +e.currentTarget.value,
              });
            }}
            type="number"
            min="1"
            max="20"
            value={isochroneParams.timeInMinutes}
            className="w-12 text-black text-center"
            name="isotime"
            id="isotime"
          />
          minutes
        </div>
      </div>
    </div>
  );
};
