import { useEffect } from "react";

const useTailwindElements = () => {
  useEffect(() => {
    const use = async () => {
      // @ts-ignore `tw-elements` package has no types available
      (await import("tw-elements")).default;
    };
    use();
  }, []);
};

export default useTailwindElements;
