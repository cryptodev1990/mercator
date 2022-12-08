import { Dispatch } from "react";
import { useStore } from "react-redux";
import { appendSearchResult } from "src/search/search-slice";
import { addLayerStyle } from "src/shapes/shape-slice";
import { OsmSearchResponse } from "src/store/search-api";

export function generateLayerId() {
  return Math.random().toString(36).substr(2, 9);
}

export function generateRandomColor() {
  return `#${Math.floor(Math.random() * 16777215).toString(16)}`;
}

export function convertHexToRGB(hex: string) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return [r, g, b];
}

export function convertRGBToHex(arr: number[]) {
  const r = arr[0].toString(16).padStart(2, "0");
  const g = arr[1].toString(16).padStart(2, "0");
  const b = arr[2].toString(16).padStart(2, "0");
  return `#${r}${g}${b}`;
}

const TAILWIND_BLUE_500 = {
  hex: "#3B82F6",
  rgb: [59, 130, 246],
};
const TAILWIND_RED_500 = {
  hex: "#EF4444",
  rgb: [239, 68, 68],
};
const TAILWIND_GREEN_500 = {
  hex: "#10B981",
  rgb: [16, 185, 129],
};
const TAILWIND_YELLOW_500 = {
  hex: "#F59E0B",
  rgb: [245, 158, 11],
};
const TAILWIND_PURPLE_500 = {
  hex: "#8B5CF6",
  rgb: [139, 92, 246],
};
const TAILWIND_PINK_500 = {
  hex: "#EC4899",
  rgb: [236, 72, 153],
};
const TAILWIND_GRAY_500 = {
  hex: "#6B7280",
  rgb: [107, 114, 128],
};

const TAILWIND_COLORS = [
  TAILWIND_BLUE_500,
  TAILWIND_RED_500,
  TAILWIND_GREEN_500,
  TAILWIND_YELLOW_500,
  TAILWIND_PURPLE_500,
  TAILWIND_PINK_500,
  TAILWIND_GRAY_500,
];

let i = 0;

export function addNewLayer(data: OsmSearchResponse, dispatch: Dispatch<any>) {
  // get number of layers already in the store
  dispatch(appendSearchResult(data));
  dispatch(
    addLayerStyle({
      id: data.query,
      lineThicknessPx: 1,
      paint: TAILWIND_COLORS[i % TAILWIND_COLORS.length].rgb,
      opacity: 1,
      type: data.label ?? "unknown",
    })
  );
  i += 1;
}
