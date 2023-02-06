import { useEffect, useState } from "react";

export const EXAMPLES = [
  "Where do people not own cars?",
  "Where do people who studied finance in college live?",
  "What's the male-female ratio in the US?",
  "Where do people who are at least 65 years old live?",
  "Where do people have gas heating?",
];

export const useFirstTimeSearch = () => {
  // TODO - this is a stub, what should first time user look like?
  const [isFirstTimeUse, setIsFirstTimeUse] = useState(true);
  const [currentExampleIdx, setCurrentExampleIdx] = useState(0);
  const [placeholderExample, setPlaceholderExample] = useState("");

  useEffect(() => {
    if (isFirstTimeUse) {
      const interval = setInterval(() => {
        setPlaceholderExample(EXAMPLES[currentExampleIdx]);
        setCurrentExampleIdx((currentExampleIdx + 1) % EXAMPLES.length);
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [isFirstTimeUse, currentExampleIdx]);

  return {
    turnOffDemo: () => setIsFirstTimeUse(false),
    placeholderExample,
    isFirstTimeUse,
  };
};
