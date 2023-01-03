import clsx from "clsx";
import { useEffect, useRef, useState } from "react";

const SliderPicker = ({
  knotSize,
  setKnotSize,
  min,
  max,
  step,
}: {
  knotSize: number;
  setKnotSize: (knotSize: number) => void;
  min?: number;
  max?: number;
  step?: string;
}) => {
  const [selected, setSelected] = useState(false);
  const [interacted, setInteracted] = useState<boolean>(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (selected && inputRef.current) {
      inputRef.current?.focus();
      inputRef.current?.select();
    } else {
      setInteracted(false);
    }
  }, [selected]);

  return (
    <div className="flex flex-row gap-2">
      {!selected && (
        <button
          onMouseDown={() => setSelected(true)}
          className={clsx(
            "bg-slate-200 hover:bg-slate-300 text-slate-800 font-bold py-2 px-4 rounded"
          )}
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <circle
              cx="12"
              cy="12"
              r={~~Math.floor(Math.sqrt(knotSize)) || 2}
            />
          </svg>
        </button>
      )}
      <div>
        <input
          ref={inputRef}
          autoFocus={selected}
          className={clsx(
            "bg-slate-200 hover:bg-slate-300 text-slate-800 font-bold py-2 px-4 rounded -rotate-90 translate-x-[-50px] transform",
            selected ? "block" : "hidden"
          )}
          onChange={(e) => {
            setKnotSize(parseFloat(e.target.value));
            setInteracted(true);
          }}
          onMouseUp={() => {
            // If the slider actually moved, then close it
            if (interacted) {
              setSelected(false);
            }
          }}
          value={knotSize}
          max={max || 100}
          min={min || 0}
          step={step || "1"}
          type="range"
        ></input>
      </div>
    </div>
  );
};

export default SliderPicker;
