import clsx from "clsx";
import { useState } from "react";
import { remark } from "remark";
import html from "remark-html";

const AnnouncementTypeEnum = {
  info: "info",
  warning: "warning",
  error: "error",
};

const CloseIcon = () => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className="h-6 w-6"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M6 18L18 6M6 6l12 12"
      />
    </svg>
  );
};

const AnnouncementBar = ({
  markdown,
  type,
}: {
  markdown: string;
  type: string;
}) => {
  // A snackbar that lists a notification and be dismissed by the useRef
  const [open, setOpen] = useState(true);
  const handleClose = () => {
    setOpen(false);
  };
  if (!open) {
    return null;
  }
  return (
    <div
      className={clsx(
        "flex flex-row justify-between items-center w-full h-12 px-4 z-10 rounded",
        type === AnnouncementTypeEnum.info && "bg-blue-500",
        type === AnnouncementTypeEnum.warning && "bg-yellow-500",
        type === AnnouncementTypeEnum.error && "bg-orange-500"
      )}
    >
      <div className="flex flex-row justify-between">
        <div className="flex flex-row">
          <div className="flex flex-row items-center">
            <div className="p-2"></div>
            <div className="p-2">
              <p
                dangerouslySetInnerHTML={{
                  __html: remark().use(html).processSync(markdown).toString(),
                }}
              ></p>
            </div>
          </div>
        </div>
      </div>
      <button onClick={handleClose}>
        <CloseIcon />
      </button>
    </div>
  );
};

export default AnnouncementBar;
