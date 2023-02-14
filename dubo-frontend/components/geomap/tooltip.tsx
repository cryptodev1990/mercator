import clsx from "clsx";
import { useMemo } from "react";
import { useTheme } from "../../lib/hooks/census/use-theme";
import useMousePosition from "../../lib/hooks/use-mouse-position";
import { pctFmtSansPct } from "./legend";

export const Tooltip = ({
  isRatio,
  zctaLookup,
  selectedColumn,
  selectedZcta,
  label,
}: {
  isRatio: boolean;
  zctaLookup: any;
  selectedColumn: any;
  selectedZcta: string;
  label: string | null;
}) => {
  const { theme } = useTheme();
  const { x, y } = useMousePosition();

  const tooltipValue = useMemo(() => {
    if (!zctaLookup) return "";
    if (!selectedZcta) return "";
    const dataRow = zctaLookup[selectedZcta];
    return dataRow;
  }, [zctaLookup, selectedZcta]);

  if (typeof tooltipValue === "undefined" || !selectedZcta) {
    return null;
  }

  const value = isRatio
    ? pctFmtSansPct(tooltipValue[selectedColumn], 2) + "%"
    : tooltipValue[selectedColumn];

  return (
    <div
      className={clsx(
        "absolute z-50 m-2",
        "rounded-md shadow-md",
        theme.bgColor
      )}
      style={{
        top: y ? y + 10 : 0,
        left: x ? x + 10 : 0,
      }}
    >
      <div className="flex flex-row justify-center items-center space-x-2 p-2">
        <div>
          <div className="font-bold">ZCTA: {selectedZcta}</div>
          <div className="font-bold">
            {label || selectedColumn}: {value}
          </div>
        </div>
      </div>
    </div>
  );
};
