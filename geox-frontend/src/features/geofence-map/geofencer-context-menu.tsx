import { useEffect, useState } from "react";

export const GeofencerContextMenu = () => {
  const [xPos, setXPos] = useState<string | null>(null);
  const [yPos, setYPos] = useState<string | null>(null);
  const [recentActivity, setRecentActivity] = useState<number>(0);

  const listenerFunc = (event: MouseEvent) => {
    event.preventDefault();
    const xPos = event.pageX - 10 + "px";
    const yPos = event.pageY - 5 + "px";
    setXPos(xPos);
    setYPos(yPos);
  };

  useEffect(() => {
    document.addEventListener("contextmenu", listenerFunc, false);

    return () => {
      document.removeEventListener("contextmenu", listenerFunc, false);
    };
  }, []);

  if (!xPos || !yPos) {
    return null;
  }

  return (
    <div
      style={{
        position: "fixed",
        top: yPos,
        left: xPos,
        zIndex: 9999,
        backgroundColor: "white",
        border: "1px solid black",
        padding: "10px",
        boxShadow: "0px 0px 10px black",
        borderRadius: "5px",
      }}
      onMouseLeave={() => {
        setXPos(null);
        setYPos(null);
      }}
      onMouseMove={() => {
        setRecentActivity(Math.random());
      }}
    >
      <div>Transform</div>
      <div>Edit</div>
      <div>Transform</div>
      <div>Transform</div>
    </div>
  );
};
