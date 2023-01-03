import clsx from "clsx";
import { TAILWIND_SLATE_50 } from "src/lib/colors";
import { ENTITY_RESOLVER } from "src/lib/entity-resolver";
import EditableLabel from "../../labels/editable-label";
import Caret from "../../icons/caret";
import { IntentResponse, ValidIntentNameEnum } from "src/store/search-api";
import { title } from "src/lib/str";

const IntentParticle = ({ text }: { text: string }) => {
  return (
    <div className="flex flex-row items-center justify-center text-slate-50">
      <div className="text-2xl">{text}</div>
    </div>
  );
};

const TaggedText = ({
  text,
  searchType,
  fillColor,
  onDropdownClick,
  onEdit,
}: {
  searchType: string;
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
        <span>{title(searchType, "_")}</span>
        <Caret onClick={(e) => onDropdownClick(e)} />
      </div>
    </div>
  );
};

function TaggedIntent({ ir }: { ir: IntentResponse }) {
  if (ir === undefined) {
    return null;
  }
  const entities = ir.parse_result.entities;
  const res = [];
  for (const entity of entities) {
    const ent = ENTITY_RESOLVER.find((e) => e.mr === entity.match_type);
    if (ent === undefined) {
      console.warn("Entity not found", entity);
      continue;
    }
    res.push(
      <TaggedText
        text={entity.matched_text ?? entity.lookup}
        onEdit={(s) => console.log(s)}
        searchType={ent?.hr}
        fillColor={ent?.fill}
        onDropdownClick={() => {
          console.log("Dropdown clicked");
        }}
      ></TaggedText>
    );
  }
  const intent = ir.intents[0];

  switch (intent) {
    case "raw_lookup": {
      return <>{res}</>;
    }
    case "area_near_constraint": {
      // loop through res and insert "within" and "," as needed
      const newRes = [];
      for (let i = 0; i < res.length; i++) {
        if (i % 2 === 0) {
          newRes.push(res[i]);
          continue;
        }
        newRes.push(<IntentParticle text={"within"} />);
        newRes.push(res[i]);
        newRes.push(<IntentParticle text={"and"} />);
      }
    }
    case "x_in_y": {
      return (
        <div className="flex flex-row">
          <div className="flex flex-row">{res[0]}</div>
          <IntentParticle text={"in"} />
          <div className="flex flex-row">{res[1]}</div>
        </div>
      );
    }
    case "x_between_y_and_z": {
      return (
        <div className="flex flex-row gap-5">
          <div className="flex flex-row gap-5">{res[0]}</div>
          <IntentParticle text={"between"} />
          <div className="flex flex-row gap-5">{res[1]}</div>
          <IntentParticle text={"and"} />
          <div className="flex flex-row gap-5">{res[2]}</div>
        </div>
      );
    }
    default: {
      return (
        <div className="flex flex-row gap-5">
          <div className="flex flex-row gap-5">{res}</div>
          <div className="flex flex-row gap-5">{res}</div>
        </div>
      );
    }
  }
}

export default TaggedIntent;
