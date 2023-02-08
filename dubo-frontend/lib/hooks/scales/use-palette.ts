import { useMemo, useState } from "react";
// @ts-ignore
import { scaleQuantile, scaleQuantize, scaleLinear } from "d3-scale";

const COLOR_BREWER_ORANGE_RED = [
  [255, 255, 178],
  [254, 217, 118],
  [253, 141, 60],
  [240, 59, 32],
  [189, 0, 38],
];

const COLOR_BREWER_BLUE_GREEN = [
  [247, 251, 255],
  [222, 235, 247],
  [107, 174, 214],
  [66, 146, 198],
  [33, 113, 181],
];

const COLOR_BREWER_BLUE_RED = [
  [247, 251, 255],
  [222, 235, 247],
  [189, 215, 231],
  [253, 219, 199],
  [244, 165, 130],
];

const COLOR_BREWER_BLUES = [
  [247, 251, 255],
  [222, 235, 247],
  [198, 219, 239],
  [158, 202, 225],
  [107, 174, 214],
];

export const PALETTES = {
  orangeRed: COLOR_BREWER_ORANGE_RED,
  blueGreen: COLOR_BREWER_BLUE_GREEN,
  blueRed: COLOR_BREWER_BLUE_RED,
  blues: COLOR_BREWER_BLUES,
};

type Palette = keyof typeof PALETTES;

export const usePalette = ({ vec }: { vec: number[] }) => {
  const [paletteName, setPaletteName] = useState<Palette>("orangeRed");
  const [scaleType, setScaleType] = useState<"quantile" | "quantize">(
    "quantize"
  );

  const rotateScaleType = () => {
    if (scaleType === "quantile") {
      setScaleType("quantize");
    } else {
      setScaleType("quantile");
    }
  };

  const isRatio = useMemo(() => {
    if (!vec) return false;
    return vec.every((d) => (d <= 1 && d >= 0) || d === null);
  }, [vec]);

  const colors = useMemo(() => {
    return PALETTES[paletteName];
  }, [paletteName]);

  const scale = useMemo(() => {
    if (!vec || vec?.length === 0) return (d: any) => [0, 0, 0];
    if (!Number.isFinite(vec[0])) {
      return (d: any) => [0, 0, 0];
    }
    if (scaleType === "quantize") {
      if (isRatio) {
        return scaleQuantize().domain([0, 1]).range(colors);
      }
      return scaleQuantize().domain(vec).range(colors);
    }
    return scaleQuantile().domain(vec).range(colors);
  }, [vec, colors, isRatio, scaleType]);

  const breaks = useMemo(() => {
    if (!vec) return [];
    const min = Math.min(...vec);
    if (scaleType === "quantize") {
      if (isRatio) {
        // return values between 0 and 1 evenly spaced
        return scaleQuantize().domain([0, 1]).ticks(5);
      }
      return scaleQuantize()
        .domain([min, Math.max(...vec)])
        .range(colors)
        .ticks(5)
        .map((d: any) => {
          // if there's a decimal, round to 2 places
          if (!d) {
            return d;
          } else if (d % 1 !== 0) {
            return d.toFixed(2);
          } else {
            return d;
          }
        });
    }
    const newBreaks = scaleQuantile().domain(vec).range(colors).quantiles();
    if (min < newBreaks[0]) newBreaks.unshift(min);
    return newBreaks.map((d: any) => {
      // if there's a decimal, round to 2 places
      if (!d) {
        return d;
      } else if (d % 1 !== 0) {
        return d.toFixed(2);
      } else {
        return d;
      }
    });
  }, [vec, colors, isRatio, scaleType]);

  return {
    scale,
    breaks,
    colors,
    setPaletteName,
    rotateScaleType,
    scaleType,
    isRatio,
  };
};
