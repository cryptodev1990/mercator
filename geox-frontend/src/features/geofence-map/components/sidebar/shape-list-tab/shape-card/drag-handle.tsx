// https://developer.mozilla.org/en-US/docs/Web/API/DataTransfer/setDragImage
import { MdDragIndicator } from "react-icons/md";
// drag handle in pure html and css
export const DragHandle = ({
  transferData,
  dragImage,
  dataTip,
}: {
  transferData: string;
  dragImage: any;
  dataTip?: string;
}) => {
  function dragStartHandler(ev: any) {
    // Set the drag's format and data. Use the event target's id for the data
    ev.dataTransfer.setData("text/plain", transferData);
    const img = new Image();
    // base64 encoded shape card
    img.src = dragImage;
    ev.dataTransfer.setDragImage(img, 30, 30);
  }

  return (
    <div data-tip={dataTip}>
      {/* Hide drag indicator behind a transparent element */}
      <div className="w-4 h-4 relative">
        <div className="w-4 h-4 absolute">
          <div
            onDragStart={dragStartHandler}
            draggable={true}
            className="absolute w-5 h-5 bg-red-0 z-10 cursor-grab"
          ></div>
          <div className="w-4 h-4">
            <MdDragIndicator className="text-gray-400 z-0" />
          </div>
        </div>
      </div>
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
  handleDragOver: (e: any) => void;
  className?: string;
  style?: any;
}) => {
  function dropHandler(ev: any) {
    ev.preventDefault();
    handleDragOver(ev);
  }

  return (
    <div
      id={id}
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e: any) => dropHandler(e)}
      style={style}
      className={className}
    >
      {children}
    </div>
  );
};
