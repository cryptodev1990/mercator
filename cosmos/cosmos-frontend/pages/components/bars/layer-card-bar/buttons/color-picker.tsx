import { convertRGBToHex } from "src/lib/colors";

const ColorPicker = ({
  color,
  setColor,
}: {
  color: number[];
  setColor: (color: string) => void;
}) => {
  if (!color || color?.length === 0) {
    return null;
  }
  const hexColor = convertRGBToHex(color);
  return (
    <div className="relative">
      <input
        type="color"
        className="z-10 w-6 h-6 absolute top-0 left-0 opacity-0"
        id="head"
        name="head"
        value={"#000000"}
        onChange={(e) => {
          console.log(e.target.value);
          setColor(e.target.value);
        }}
      />
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
          d="M5 15l7-7 7 7M5 21l7-7 7 7"
        />
      </svg>
    </div>
  );
};

export default ColorPicker;
