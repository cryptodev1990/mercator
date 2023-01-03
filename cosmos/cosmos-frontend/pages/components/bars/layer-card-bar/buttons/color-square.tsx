import { convertRGBToHex } from "src/lib/colors";

const ColorSquare = ({ color }: { color: number[] }) => {
  if (color === undefined) {
    return null;
  }
  const hexColor = convertRGBToHex(color);
  return (
    <div className="relative">
      <svg
        className="w-6 h-6"
        fill={hexColor.toUpperCase()}
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M10 10 L90 10 L90 90 L10 90 Z"
        />
      </svg>
    </div>
  );
};

export default ColorSquare;
