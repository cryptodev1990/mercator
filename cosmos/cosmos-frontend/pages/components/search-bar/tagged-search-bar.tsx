import clsx from "clsx";
import { useEffect, useRef, useState } from "react";
import {
  selectSearchState,
  setInputText,
} from "../../../src/search/search-slice";
import { useDispatch, useSelector } from "react-redux";
import { useOsmQueryGetQuery } from "src/store/search-api";
import { addNewLayer } from "src/lib/add-new-layer";
import { ENTITY_RESOLVER } from "src/lib/entity-resolver";
import { TAILWIND_COLORS, TAILWIND_SLATE_50 } from "src/lib/colors";
import EditableLabel from "./editable-label";

const Caret = ({
  onClick,
}: {
  onClick: (e: React.MouseEvent<HTMLDivElement, MouseEvent>) => void;
}) => {
  return (
    <div onClick={onClick}>
      <svg
        className="w-4 h-4"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 20 20"
        fill="currentColor"
      >
        <path
          fillRule="evenodd"
          d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
          clipRule="evenodd"
        />
      </svg>
    </div>
  );
};

// choose one element at random from an arrray
function nab(arr: string[]) {
  return arr[Math.floor(Math.random() * arr.length)];
}

const IntentParticle = ({ text }: { text: string }) => {
  return (
    <div className="flex flex-row items-center justify-center text-black">
      <div className="text-2xl">{text}</div>
    </div>
  );
};

const TaggedText = ({
  text,
  tagId,
  fillColor,
  onDropdownClick,
  onEdit,
}: {
  tagId: string;
  fillColor?: string;
  onDropdownClick: (e: React.MouseEvent<HTMLDivElement, MouseEvent>) => void;
  onEdit: (value: string) => void;
  text: string;
}) => {
  return (
    <div
      className={clsx(
        "flex flex-row px-10 py-2 rounded-full gap-5 border-4 cursor-pointer items-center justify-start"
      )}
      style={{
        background: TAILWIND_SLATE_50.hex,
        color: fillColor,
        borderColor: fillColor,
      }}
    >
      <div className="text-2xl">
        <EditableLabel value={text} onChange={(s) => onEdit(s)} />
      </div>
      <div
        className={clsx(
          "border text-sm px-2 rounded-full",
          "flex-none ml-auto flex flex-row items-center"
        )}
        style={{ background: fillColor, color: TAILWIND_SLATE_50.hex }}
      >
        <span>{tagId}</span>
        <Caret onClick={(e) => onDropdownClick(e)} />
      </div>
    </div>
  );
};

const TaggedSearchBar = () => {
  const [localInputText, setLocalInputText] = useState<string>("");
  const [timeElapsed, setTimeElapsed] = useState<number>(0);
  const isLoading = false;
  // within-component copy of query text

  useEffect(() => {
    // if the query is loading, start the timer
    let interval: NodeJS.Timeout;
    if (isLoading) {
      setTimeElapsed(0);
      interval = setInterval(() => {
        setTimeElapsed((prev) => prev + 1);
      }, 1000);
    }
    return () => {
      clearInterval(interval);
    };
  }, [isLoading]);

  return (
    <div className="flex flex-col justify-start items-center space-y-10">
      <div className="border border-slate-200 rounded h-12 px-4 z-10 w-full bg-slate-200 relative flex flex-row">
        <div className="absolute top-0 left-0 flex flex-row m-0 p-0 h-full w-full gap-2">
          <>
            <TaggedText
              text={"Random thing"}
              onEdit={(s) => setLocalInputText(s)}
              tagId={nab(
                ENTITY_RESOLVER.map((e) => {
                  return e.hr;
                })
              )}
              fillColor={nab(
                ENTITY_RESOLVER.map((e) => {
                  return e.fill;
                })
              )}
              onDropdownClick={() => {
                console.log("Dropdown clicked");
              }}
            ></TaggedText>
            <IntentParticle text={"in"} />
            <TaggedText
              text={"Fake Data Town"}
              onEdit={(s) => setLocalInputText(s)}
              tagId={nab(
                ENTITY_RESOLVER.map((e) => {
                  return e.hr;
                })
              )}
              fillColor={nab(
                ENTITY_RESOLVER.map((e) => {
                  return e.fill;
                })
              )}
              onDropdownClick={() => {
                console.log("Dropdown clicked");
              }}
            ></TaggedText>
          </>
          <button
            className={clsx(
              "flex-none ml-auto p-1 px-5 bg-purple-500 rounded w-40 h-full text-slate-50",
              isLoading && "animate-pulse"
            )}
            onClick={(e) => {
              console.log("Locate button clicked");
            }}
          >
            {isLoading ? `${timeElapsed} sec` : "Locate"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default TaggedSearchBar;
