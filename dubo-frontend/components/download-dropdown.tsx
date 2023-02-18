import clsx from "clsx";
import { useState, useRef, useEffect } from "react";
import { MdDownload } from "react-icons/md";

const DropdownItem = ({
  onClick,
  text,
}: {
  onClick: () => void;
  text: string;
}) => (
  <li>
    <a
      className="
        dropdown-item
        text-sm
        py-2
        px-4
        font-normal
        block
        w-full
        whitespace-nowrap
        bg-transparent
        text-gray-700
        hover:bg-gray-100
        cursor-pointer
      "
      onClick={onClick}
    >
      {text}
    </a>
  </li>
);

const DownloadDropdown = ({
  handleCSVExport,
  handleJSONExport,
  theme,
}: {
  handleCSVExport: () => void;
  handleJSONExport: () => void;
  theme?: { theme: string; bgColor: string; secondaryBgColor: string };
}) => {
  const dropdownRef = useRef<HTMLDivElement | null>(null);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        event.target &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [dropdownRef]);

  return (
    <div className="flex justify-center">
      <div>
        <div className="relative" ref={dropdownRef}>
          <button
            className={clsx(
              "border font-bold py-1.5 px-3 transition flex items-center",
              (theme && theme?.theme?.startsWith("light")) || !theme
                ? "border-spBlue text-spBlue hover:bg-gray-100"
                : `border-spWhite text-white ${theme?.bgColor} hover:${theme?.secondaryBgColor}`
            )}
            type="button"
            onClick={() => {
              if (!isDropdownOpen) {
                setIsDropdownOpen(!isDropdownOpen);
              }
            }}
          >
            <MdDownload />
          </button>
          <ul
            className={clsx(
              `
              z-50
              py-2 mt-1 m-0
              min-w-max
              absolute
              bg-white
              border border-gray-200
              !right-0 !left-auto
              text-base
              float-left
              list-none
              text-left
              shadow-md
              bg-clip-padding
            `,
              !isDropdownOpen && "hidden"
            )}
          >
            <DropdownItem onClick={handleCSVExport} text={"CSV"} />
            <DropdownItem onClick={handleJSONExport} text={"JSON"} />
          </ul>
        </div>
      </div>
    </div>
  );
};
export default DownloadDropdown;
