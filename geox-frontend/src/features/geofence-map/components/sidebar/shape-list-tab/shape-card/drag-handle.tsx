// https://developer.mozilla.org/en-US/docs/Web/API/DataTransfer/setDragImage
import React, { useRef } from "react";
import { GeoShape, GeoShapeMetadata } from "../../../../../../client";
import { DragIndicatorIcon } from "../../../../../../common/components/icons";
import NamespaceMenu from "../../namespace-menu";
// drag handle in pure html and css
export const DragHandle = ({
  shape,
  dragImage,
}: {
  shape: GeoShapeMetadata;
  dragImage: any;
}) => {
  const outerRef = useRef<HTMLDivElement>(null);

  function dragStartHandler(ev: any) {
    // Set the drag's format and data. Use the event target's id for the data
    ev.dataTransfer.setData("text/plain", shape.uuid);
    const img = new Image();
    // base64 encoded shape card
    img.src = dragImage;
    ev.dataTransfer.setDragImage(img, 30, 30);
  }

  return (
    <div
      className="w-4 h-4 cursor-grab"
      onDragStart={dragStartHandler}
      draggable={true}
      ref={outerRef}
    >
      <DragIndicatorIcon className="transform text-gray-400 hover:text-red-300 hover:translate-y-[-1px]" />
      <NamespaceMenu outerRef={outerRef} shape={shape} />
    </div>
  );
};

export const DragTarget = ({
  id,
  children,
  handleDragOver,
  className,
  style,
  ...props
}: {
  id: string;
  children: any;
  handleDragOver: (e: React.DragEvent) => void;
  className?: string;
  style?: React.CSSProperties;
}) => {
  function dropHandler(ev: any) {
    ev.preventDefault();
    handleDragOver(ev);
  }

  return (
    <div
      id={id}
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e: React.DragEvent<HTMLDivElement>) => dropHandler(e)}
      style={style}
      className={className}
    >
      {children}
    </div>
  );
};
