import { useState } from "react";

export const useTooltip = () => {
  // TODO How do I alert if no tooltip is modified?
  // Needs a Tooltip component in the React DOM to work
  const [tooltip, showTooltip] = useState(false);

  const tooltipEvents = {
    onMouseEnter: () => showTooltip(true),
    onMouseLeave: () => {
      showTooltip(false);
      setTimeout(() => showTooltip(true), 50);
    },
  };
  return { tooltip, showTooltip, tooltipEvents };
};
