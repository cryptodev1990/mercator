import SliderPicker from "./slider-picker";

const RadiusPicker = ({
  radius,
  setRadius,
}: {
  radius: number;
  setRadius: (radius: number) => void;
}) => {
  return <SliderPicker knotSize={radius} setKnotSize={setRadius} />;
};

export default RadiusPicker;
