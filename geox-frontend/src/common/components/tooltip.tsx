// NOTE: There's probably a better tooltip library
// Only works on elements that are DOM-based (so not deck.gl)
// Also doesn't work in Virtuoso
import { useEffect, useRef, useState } from "react";

function getX(rect: any, skew: string) {
  // get the x position of the element if the element were pointed right
  if (skew === "left") {
    console.log("left");
    return rect.left;
  } else if (skew === "right") {
    return rect.right;
  } else {
    return rect.left + rect.width / 2;
  }
}

export function Tooltip() {
  const [tooltip, setTooltip] = useState<string | null>(null);
  const [posX, setPosX] = useState<number | null>(null);
  const [posY, setPosY] = useState<number | null>(null);
  const [skew, setSkew] = useState<string>("left");
  const [cxOffset, setCxOffset] = useState<number>(0);
  const [renderCount, setRenderCount] = useState(0);
  const allElRef = useRef<Element[]>([]);

  const tooltipWidth = 50;
  const tooltipHeight = 50;

  useEffect(() => {
    const tips = document.querySelectorAll("[data-tip]");
    allElRef.current = Array.from(tips);
    for (const el of allElRef.current) {
      el.addEventListener("mouseover", (e) => {
        const elRect = el.getBoundingClientRect();
        const x = getX(elRect, skew);
        const y = elRect.top + elRect.height / 2 - tooltipHeight / 2;
        e.preventDefault();
        const ttText = el.getAttribute("data-tip");
        const ttSkew = el.getAttribute("data-tip-skew") || "left";
        const cxOffsetTmp = el.getAttribute("data-tip-cx") || "0";
        setCxOffset(parseInt(cxOffsetTmp));
        setSkew(ttSkew);
        setTooltip(ttText || "");
        setPosX(() => x);
        setPosY(() => y);
      });
      el.addEventListener("mouseout", (e) => {
        setTooltip(null);
        setPosX(null);
        setPosY(null);
      });
    }
    return () => {
      for (const el of allElRef.current) {
        el.removeEventListener("mouseover", () => {});
        el.removeEventListener("mouseout", () => {});
      }
    };
  }, [renderCount, skew]);

  // poll document until all data-tip elements are loaded
  useEffect(() => {
    const interval = setInterval(() => {
      // const tips = document.querySelectorAll("[data-tip]");
      // jif (tips.length > 0 && tips.length === allElRef.current.length) {
      // j  clearInterval(interval);
      // j} else {
      setRenderCount((prev) => prev + 1);
      // }
    }, 250);
    return () => clearInterval(interval);
  }, []);

  return (
    <div
      className="rounded p-3 block text-sm"
      style={{
        position: "absolute",
        minWidth: tooltipWidth,
        top: `${posY}px`,
        left: `${(posX || 0) - cxOffset}px`,
        margin: "1rem",
        float: skew !== "left" ? "left" : "right",
        minHeight: tooltipHeight,
        visibility: tooltip ? "visible" : "hidden",
        lineHeight: "1.5rem",
        whiteSpace: "pre-wrap",
        textAlign: "center",
        zIndex: 10000,
        color: "#fff",
        pointerEvents: "none",
        backgroundColor: "rgba(0,0,0,0.8)",
      }}
    >
      <h1>{tooltip}</h1>
    </div>
  );
}
